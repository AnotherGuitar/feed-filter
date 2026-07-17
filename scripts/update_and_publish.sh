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

if [ "$status" -eq 2 ]; then
    osascript -e 'display notification "One or more channels were skipped after repeated failures - check ~/Library/Logs/feed-filter/update.err.log" with title "feed-filter" sound name "Basso"'
elif [ "$status" -ne 0 ]; then
    osascript -e 'display notification "feed-filter failed unexpectedly - check ~/Library/Logs/feed-filter/update.err.log" with title "feed-filter" sound name "Basso"'
fi
