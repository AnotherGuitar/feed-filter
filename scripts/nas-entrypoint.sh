#!/bin/bash
set -euo pipefail

echo "$(date -u +%FT%TZ) nas-entrypoint: starting supercronic with schedule from scripts/nas-crontab"
exec /usr/local/bin/supercronic /repo/scripts/nas-crontab
