#!/bin/bash
set -euo pipefail

# Runs inside the feed-filter-nas Docker container (see Dockerfile.nas), with
# the NAS's checkout of this repo bind-mounted at /repo and GITHUB_TOKEN
# injected via --env-file. Scheduled by QNAP Task Scheduler - see README.md
# "NAS automation" section for the full setup.
cd /repo

git config --global --add safe.directory /repo
git config user.name "Chris Davis"
git config user.email "AnotherGuitar@users.noreply.github.com"

ts="$(date +%Y-%m-%d-%H-%M)"
mkdir -p logs

# Prune logs older than 30 days so this directory doesn't grow forever.
find logs -type f \( -name 'run-*.log' -o -name 'summary-*.txt' \) -mtime +30 -delete

# Pick up anything pushed from elsewhere (e.g. the laptop) before we start,
# so we're not building on a stale base and don't create a needless conflict.
git pull --rebase origin main

uv sync --all-extras

overall_status=0
for config in configs/*.yaml; do
    topic="$(basename "$config" .yaml)"
    summary_path="logs/summary-${topic}-${ts}.txt"

    if uv run feed-filter --config "$config" --summary-path "$summary_path"; then
        status=0
    else
        status=$?
    fi

    if [ "$status" -ne 0 ] && [ "$status" -ge "$overall_status" ]; then
        overall_status=$status
    fi
done

git add docs/
if git diff --cached --quiet; then
    echo "No changes to commit"
else
    git commit -m "Update filtered feeds"
    git push "https://x-access-token:${GITHUB_TOKEN}@github.com/AnotherGuitar/feed-filter.git" HEAD:main

    # Ping the WebSub hub now that the new content is actually live, so
    # hub-aware readers (e.g. Feedly) get it without waiting on their own
    # polling schedule.
    for config in configs/*.yaml; do
        uv run feed-filter --config "$config" --ping-hub
    done
fi

exit "$overall_status"
