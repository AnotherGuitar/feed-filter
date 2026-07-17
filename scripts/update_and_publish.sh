#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

/usr/local/bin/uv sync --python 3.13 --all-extras
/usr/local/bin/uv run feed-filter --config channels.yaml

git add docs/
if git diff --cached --quiet; then
    echo "No changes to commit"
else
    git commit -m "Update filtered feeds"
    git push
fi
