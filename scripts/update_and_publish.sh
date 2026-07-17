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

    # Ping the WebSub hub now that the new content is actually live, so
    # hub-aware readers (e.g. Feedly) get it without waiting on their own
    # polling schedule.
    for config in configs/*.yaml; do
        /usr/local/bin/uv run feed-filter --config "$config" --ping-hub
    done

    # Feedly appears to cache by the final resolved URL rather than
    # re-polling, ignoring WebSub/manual refresh - bumping a cache-busting
    # query param on the redirect's target (while keeping the Netlify entry
    # URL itself permanently stable) forces it to see a "new" URL and fetch
    # fresh content instead of serving what it cached before. One redirect
    # per config file that defines a combined_output.
    : > netlify-redirect/_redirects
    for config in configs/*.yaml; do
        topic="$(basename "$config" .yaml)"
        combined_output="$(python3 -c "import yaml; print(yaml.safe_load(open('$config')).get('combined_output') or '')")"
        if [ -n "$combined_output" ]; then
            echo "/combined-${topic}.xml  https://raw.githubusercontent.com/AnotherGuitar/feed-filter/main/${combined_output}?v=${ts}  302" >> netlify-redirect/_redirects
        fi
    done
    git add netlify-redirect/_redirects
    if git diff --cached --quiet; then
        echo "No redirect change to commit"
    else
        git commit -m "Bump Netlify redirect cache-busting version"
        git push
    fi
    (cd netlify-redirect && /Users/Chris/.nvm/versions/node/v22.19.0/bin/netlify deploy --prod --dir=.)
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
