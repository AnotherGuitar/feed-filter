#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Refuse to run if another invocation is already in progress - two processes
# writing to the same working tree at once is a real hazard (see
# update_and_publish_nas.sh, which hit exactly this with the NAS's own
# scheduled runs). mkdir is atomic on any POSIX filesystem, so this doesn't
# need flock (not installed on macOS by default, unlike the NAS's Linux
# container).
lock_dir="/tmp/feed-filter-update-and-publish.lock.d"
if ! mkdir "$lock_dir" 2>/dev/null; then
    echo "another run is already in progress - skipping this invocation"
    exit 0
fi
trap 'rmdir "$lock_dir" 2>/dev/null' EXIT

ts="$(date +%Y-%m-%d-%H-%M)"
run_log="logs/run-${ts}.log"
mkdir -p logs

# Prune logs older than 30 days so this directory doesn't grow forever.
find logs -type f \( -name 'run-*.log' -o -name 'summary-*.txt' \) -mtime +30 -delete

exec > "$run_log" 2>&1

# Defensive: recover from a stuck rebase/merge left by a previous run that
# hit a conflict and couldn't finish cleanly - otherwise every future run
# fails at this same step forever, since git refuses to pull with one
# already in progress.
if [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
    echo "found a stuck rebase from a previous run - aborting it"
    git rebase --abort || true
fi
if [ -f .git/MERGE_HEAD ]; then
    echo "found a stuck merge from a previous run - aborting it"
    git merge --abort || true
fi

# Pick up anything pushed from elsewhere (e.g. the NAS) before we start, so
# we're not building on a stale base and don't create a needless conflict.
git pull --rebase origin main

/usr/local/bin/uv sync --python 3.13 --all-extras

overall_status=0
last_summary=""
for config in configs/*.yaml; do
    topic="$(basename "$config" .yaml)"
    summary_path="logs/summary-${topic}-${ts}.txt"

    if /usr/local/bin/uv run feed-filter --config "$config" --summary-path "$summary_path"; then
        status=0
    else
        status=$?
    fi

    if [ "$status" -ne 0 ] && [ "$status" -ge "$overall_status" ]; then
        overall_status=$status
        last_summary="$summary_path"
    fi
done

git add docs/
if git diff --cached --quiet; then
    echo "No changes to commit"
else
    git commit -m "Update filtered feeds"

    # The run above can take a while across every channel, long enough that
    # something else (e.g. the NAS) can push to main in the meantime,
    # rejecting this push as non-fast-forward. docs/ is pure regenerated
    # output with no hand-edited content, so there's nothing to meaningfully
    # merge - if we lost the race, just discard our redundant commit rather
    # than rebasing (which can itself conflict and leave the repo stuck
    # mid-rebase for every future run). The next scheduled run (NAS or this
    # one) regenerates fresh anyway.
    if git push; then
        # Ping the WebSub hub now that the new content is actually live, so
        # hub-aware readers (e.g. Feedly) get it without waiting on their own
        # polling schedule.
        for config in configs/*.yaml; do
            /usr/local/bin/uv run feed-filter --config "$config" --ping-hub
        done
    else
        echo "push rejected - someone else published first; discarding this run's commit"
        git fetch origin
        git reset --hard origin/main
    fi
fi

repo_dir="$(pwd)"

if [ "$overall_status" -eq 2 ]; then
    terminal-notifier -title "feed-filter" \
        -message "One or more channels were skipped after repeated failures - click for details" \
        -sound Basso \
        -open "file://${repo_dir}/${last_summary}"
elif [ "$overall_status" -ne 0 ]; then
    terminal-notifier -title "feed-filter" \
        -message "feed-filter failed unexpectedly - click for the error log" \
        -sound Basso \
        -open "file://${repo_dir}/${run_log}"
fi
