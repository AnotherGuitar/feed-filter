#!/bin/bash
set -euo pipefail

# GITHUB_TOKEN arrives via `docker run --env-file`, but cron does not carry
# the container's environment into the jobs it spawns - scripts/nas-crontab
# explicitly sources this file instead. Written fresh to the container's own
# filesystem (never into the bind-mounted repo), so the token never touches
# the NAS share or git history.
echo "export GITHUB_TOKEN=${GITHUB_TOKEN}" > /etc/environment

cp /repo/scripts/nas-crontab /etc/cron.d/feed-filter
chmod 0644 /etc/cron.d/feed-filter

echo "$(date -u +%FT%TZ) nas-entrypoint: schedule installed, starting cron in foreground"
exec cron -f
