#!/bin/bash
# FINAL2.sh : ONE heavy job on the final snapshot H3: GATES.sh, then the byte-diff + mirror sweep and the compare
# against the L20 base sweep (logs/G/base). cwd = H3 root.
export TMPDIR=/home/fabrice/git/pycsl-u72/scratchpad/u72/tmp; mkdir -p $TMPDIR
U=/home/fabrice/git/pycsl-u72/scratchpad/u72; H3=/home/fabrice/git/pycsl-u72-h3
echo "FINAL2 start $(date -u) $(git -C $H3 rev-parse --short HEAD) df: $(df -m /tmp | tail -1)"
GT=$H3 bash $U/tools/GATES.sh $U/logs/GATES3
bash $U/tools/S.sh $H3 $U/logs/G/h3
bash $U/tools/CMP.sh $U/logs/G/base $U/logs/G/h3 $U/logs/G/C3
echo "FINAL2 end $(date -u)"
