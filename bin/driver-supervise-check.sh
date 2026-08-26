#!/usr/bin/env bash
# Supervisor liveness probe for the self-tcb-reduction-driver 96h delegated run.
# Prints a compact verdict block. Decides nothing itself; the supervising session
# reads VERDICT and relaunches ONLY on DEAD (never on ALIVE -- two concurrent
# drivers corrupt increments, cf. SKILL A.2.4 ownerless-writer lesson).
cd "$(dirname "$0")/.." || exit 2
NOW=$(date +%s)
DL=$(cat getting-better/.driver-deadline 2>/dev/null || echo 0)
echo "now=$NOW deadline=$DL left_min=$(( (DL-NOW)/60 ))"
[ "$NOW" -ge "$DL" ] && { echo "VERDICT=DEADLINE"; exit 0; }

# (a) any live repo-writing worker? (proof / census / sweep)
WORKERS=$(ps -eo pid,ppid,etimes,cmd \
  | grep -E 'pycsl\.py|why3|byte-diff-sweep|self-annotate|sweep\.py' \
  | grep -v grep | grep -vc '^$')
echo "live_workers=$WORKERS"
ps -eo pid,etimes,cmd | grep -E 'pycsl\.py|why3|byte-diff-sweep' | grep -v grep | head -3

# (b) recent repo progress (commits are the durable per-increment signal, A.2.4)
LASTC=$(git log -1 --format=%ct 2>/dev/null || echo 0)
echo "last_commit_age_min=$(( (NOW-LASTC)/60 ))  head=$(git log -1 --format='%h %s' | cut -c1-90)"
PLOG=getting-better/driver-progress.log
[ -f "$PLOG" ] && echo "progress_log_age_min=$(( (NOW-$(stat -c %Y "$PLOG"))/60 ))"

# (c) tree hygiene: dirty mirror + stray .bak = a dead census left garbage
echo "dirty_self_annotate=$(git status --porcelain src/self-annotate/ | wc -l)"
echo "stray_bak=$(find src/self-annotate -name '*.py.bak' 2>/dev/null | wc -l)"
echo "trusted_count=$(for f in $(find src/self-annotate/src -name '*.py'); do grep -cF '\trusted' "$f"; done | paste -sd+ | bc)"

if [ "$WORKERS" -gt 0 ]; then echo "VERDICT=ALIVE (worker running)"; else echo "VERDICT=NOWORKER"; fi
