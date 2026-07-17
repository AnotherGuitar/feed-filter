#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

/usr/local/bin/uv sync --python 3.13 --all-extras

if /usr/local/bin/uv run feed-filter --config channels.yaml; then
    status=0
else
    status=$?
fi

git add docs/
if git diff --cached --quiet; then
    echo "No changes to commit"
else
    git commit -m "Update filtered feeds"
    git push
fi

repo_dir="$(pwd)"

if [ "$status" -eq 2 ]; then
    terminal-notifier -title "feed-filter" \
        -message "One or more channels were skipped after repeated failures - click for details" \
        -sound Basso \
        -open "file://${repo_dir}/logs/last_run_summary.txt"
elif [ "$status" -ne 0 ]; then
    terminal-notifier -title "feed-filter" \
        -message "feed-filter failed unexpectedly - click for the error log" \
        -sound Basso \
        -open "file://${repo_dir}/logs/update.err.log"
fi
