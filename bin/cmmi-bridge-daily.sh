#!/usr/bin/env bash
# cmmi-bridge-daily.sh — cron-friendly daily bridge run.
#
# Starts the 2-week dual-write clock that gates Item 3.4 of
# cmmi-tailoring-plan-follow-up-2.md (supervisor reader switch from
# metrics/logs/ to projects/pycsl/message-queues/).
#
# Bounds volume via --max-age-days 30: avoids re-mirroring the
# 81k-message backlog on every run.
#
# Cron entry (Mondays through Sundays at 05:00):
#   0 5 * * * cd ~/git/pycsl && bin/cmmi-bridge-daily.sh >> metrics/cron.log 2>&1
#
# Uses flock to prevent overlapping runs; safe to invoke faster than
# the bridge can complete.

set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
cd "$REPO_ROOT"

LOCK_FILE="metrics/.cmmi-bridge-daily.lock"
mkdir -p "$(dirname "$LOCK_FILE")"
exec 200>"$LOCK_FILE"
if ! flock -n 200; then
    echo "cmmi-bridge-daily: another bridge run is in progress; skipping" >&2
    exit 0
fi

echo "[cmmi-bridge-daily] $(date -u '+%Y-%m-%dT%H:%M:%SZ') — starting"
bin/cmmi-msg-bridge.py --max-age-days 30
echo "[cmmi-bridge-daily] $(date -u '+%Y-%m-%dT%H:%M:%SZ') — done"
