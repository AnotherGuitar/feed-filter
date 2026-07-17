#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

ts="$(date +%Y-%m-%d-%H-%M)"
run_log="logs/run-${ts}.log"
mkdir -p logs

# Prune logs older than 30 days so this directory doesn't grow forever.
find logs -type f \( -name 'run-*.log' -o -name 'summary-*.txt' \) -mtime +30 -delete

exec > "$run_log" 2>&1

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
    git push
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
