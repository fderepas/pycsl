#!/bin/bash
# heavy.sh <cmd...> : run a HEAVY job (why3/pycsl whole-file proof, corpus/pyref/mirror sweep, coqc, lake)
# under a global semaphore AND a capped systemd scope (MemoryMax=6G, no MemoryHigh), per the OOM rule
# (4 session deaths = systemd-oomd killing the whole tmux scope). rc 137/143 = killed: a RESOURCE
# failure, re-run it; never a proof verdict.
# Classes (auto-detected from the command line; HEAVY_LOW=1 forces LOW):
#   QUICK  -- `--no-proof` / `--type-only` / `--typecheck` runs: own tiny slot 3, never waits behind proofs.
#   LOW    -- a pycsl.py whole-file proof of a src/self-annotate mirror file (no --no-proof / --fun), or a
#             `why3 prove` of a mirror .mlw: slot 2 ONLY, so slot 1 always serves short GATING jobs.
#   NORMAL -- everything else (spikes, witnesses, sweeps, planes): slot 1 or 2, FIFO-ish via gate.lock.
# NEVER edit this file in place while jobs are queued: write a new file and `mv` it over (atomic rename).
D=/home/fabrice/git/pycsl/scratchpad/heavy
ARGS=" $* "
CLASS=NORMAL
case "$ARGS" in *" --no-proof "*|*" --type-only "*|*" --typecheck "*) CLASS=QUICK ;; esac
if [ "$CLASS" = NORMAL ]; then
  if [[ "$ARGS" == *pycsl.py* && "$ARGS" == *self-annotate/src/*.py* && "$ARGS" != *" --fun "* ]]; then CLASS=LOW; fi
  if [[ "$ARGS" == *"why3 prove"* && "$ARGS" == *.mlw* && ( "$ARGS" == *self-annotate* || "$ARGS" == *mir* ) ]]; then CLASS=LOW; fi
fi
[ -n "$HEAVY_LOW" ] && CLASS=LOW
case $CLASS in QUICK) SLOTS="3" ;; LOW) SLOTS="2" ;; *) SLOTS="1 2" ;; esac
exec {g}>"$D/gate.lock"
[ "$CLASS" = NORMAL ] && flock "$g"
while true; do
  for s in $SLOTS; do
    exec {fd}>"$D/slot$s.lock"
    if flock -n "$fd"; then
      [ "$CLASS" = NORMAL ] && flock -u "$g"; exec {g}>&-
      systemd-run --user --scope -q -p MemoryMax=6G -- "$@"
      rc=$?
      flock -u "$fd"; exec {fd}>&-
      exit $rc
    fi
    exec {fd}>&-
  done
  sleep 3
done
