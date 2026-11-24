#!/bin/bash
# live.sh : u67 liveness, every 10 min, until scratchpad/u67/STOP exists
while [ ! -f /home/fabrice/git/pycsl-u67/scratchpad/u67/STOP ]; do
  echo "$(date -u) u67 alive: base=$(cat /home/fabrice/git/pycsl-u67/scratchpad/u67/sw/base/done.txt 2>/dev/null | tr '\n' ' ') bdfiles=$(ls /home/fabrice/git/pycsl-u67/scratchpad/u67/sw/base/bd 2>/dev/null | wc -l) proofs=$(tail -1 /home/fabrice/git/pycsl-u67/scratchpad/u67/pr/summary.txt 2>/dev/null | cut -c1-120) G=$(tail -1 /home/fabrice/git/pycsl-u67/scratchpad/u67/logs/G.out 2>/dev/null | cut -c1-120)" >> /home/fabrice/git/pycsl-u67/progress.txt
  for i in $(seq 60); do [ -f /home/fabrice/git/pycsl-u67/scratchpad/u67/STOP ] && break; sleep 10; done
done
