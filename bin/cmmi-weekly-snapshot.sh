#!/usr/bin/env bash
# cmmi-weekly-snapshot.sh — cron-friendly weekly KPI snapshot.
#
# Calls bin/cmmi-metrics-ingest.py --weekly to append one row to
# projects/pycsl/docs/metrics/metrics-store.json. Designed to be
# invoked by cron (Mondays 06:00) — see Snapshot Schedule in
# projects/pycsl/PROJECT.md.
#
# Exits non-zero if the ingest fails so cron alerts the developer
# (per Item 4 risk mitigation in cmmi-tailoring-plan-follow-up.md).
#
# Output written to projects/pycsl/docs/metrics/ and to the
# stdout/stderr capture the cron entry redirects to metrics/cron.log.

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$HERE/.." && pwd)"
cd "$REPO_ROOT"

# Use flock to prevent concurrent runs if cron fires faster than the
# previous invocation completes (defensive — should never happen at
# weekly cadence, but protects the metrics-store.json from races).
LOCK_FILE="metrics/.cmmi-weekly-snapshot.lock"
mkdir -p "$(dirname "$LOCK_FILE")"

exec 200>"$LOCK_FILE"
if ! flock -n 200; then
    echo "cmmi-weekly-snapshot: another snapshot run is in progress; skipping" >&2
    exit 0
fi

echo "[cmmi-weekly-snapshot] $(date -u '+%Y-%m-%dT%H:%M:%SZ') — starting"
bin/cmmi-metrics-ingest.py --weekly
echo "[cmmi-weekly-snapshot] $(date -u '+%Y-%m-%dT%H:%M:%SZ') — done"
