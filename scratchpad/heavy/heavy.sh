#!/bin/bash
# heavy.sh <cmd...> : run a HEAVY job (why3/pycsl whole-file proof, corpus/pyref/mirror sweep, coqc, lake)
# under a global 2-slot semaphore AND a capped systemd scope (MemoryMax=6G, no MemoryHigh), per the OOM rule
# (4 session deaths = systemd-oomd killing the whole tmux scope). rc 137 = OOM-kill: a RESOURCE
# failure, re-run it; never a proof verdict.
# Fairness: a waiter first takes the GATE lock (blocking), then waits for a free slot while holding
# it, so a queue that relaunches immediately cannot starve earlier waiters.
D=/home/fabrice/git/pycsl/scratchpad/heavy
exec {g}>"$D/gate.lock"
flock "$g"
while true; do
  for s in 1 2; do
    exec {fd}>"$D/slot$s.lock"
    if flock -n "$fd"; then
      flock -u "$g"; exec {g}>&-
      systemd-run --user --scope -q -p MemoryMax=6G -- "$@"
      rc=$?
      flock -u "$fd"; exec {fd}>&-
      exit $rc
    fi
    exec {fd}>&-
  done
  sleep 3
done
