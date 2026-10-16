#!/bin/bash
# heavy.sh <cmd...> : run a HEAVY job (why3/pycsl whole-file proof, corpus/pyref/mirror sweep, coqc, lake)
# under a global 2-slot semaphore AND a capped systemd scope (MemoryMax=6G, no MemoryHigh), per the OOM rule
# (4 session deaths = systemd-oomd killing the whole tmux scope). rc 137 = OOM-kill: a RESOURCE
# failure, re-run it; never a proof verdict.
# Fairness: a waiter first takes the GATE lock (blocking), then waits for a free slot while holding
# it, so a queue that relaunches immediately cannot starve earlier waiters.
# Priority: HEAVY_LOW=1 (long whole-file re-proof queues) may only take slot 2, so slot 1 is
# always reserved for short GATING jobs (spikes, witnesses, sweeps, planes). A LOW waiter does
# not hold the gate while it waits, so it never blocks a short job queued behind it.
D=/home/fabrice/git/pycsl/scratchpad/heavy
SLOTS="1 2"; [ -n "$HEAVY_LOW" ] && SLOTS="2"
exec {g}>"$D/gate.lock"
[ -z "$HEAVY_LOW" ] && flock "$g"
while true; do
  for s in $SLOTS; do
    exec {fd}>"$D/slot$s.lock"
    if flock -n "$fd"; then
      [ -z "$HEAVY_LOW" ] && flock -u "$g"; exec {g}>&-
      systemd-run --user --scope -q -p MemoryMax=6G -- "$@"
      rc=$?
      flock -u "$fd"; exec {fd}>&-
      exit $rc
    fi
    exec {fd}>&-
  done
  sleep 3
done
