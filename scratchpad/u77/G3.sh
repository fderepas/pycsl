#!/bin/bash
# G3.sh: after the S default-field fix (10532 / 10535 / zu77a), on pycsl-u77h at the fix commit: witnesses again + the corpus-reading planes individually.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u77/scratchpad/u77/tmp
U=/home/fabrice/git/pycsl-u77/scratchpad/u77; H=/home/fabrice/git/pycsl-u77h; G=$U/logs/G3; mkdir -p $G
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
cd $H || exit 2; echo "G3 start $(date -u) $(git log --oneline -1 | cut -c1-12) $(grep oom_kill $EV)"
$U/wit.sh hs3:$H
for p in check-corpus-contract-truth check-corpus-executes check-corpus-contract-truth-args check-claim-vacuity check-refusal-witness-coverage; do
  python3 bin/$p.py > $G/$p.txt 2>&1; echo "$p rc=$? $(tail -1 $G/$p.txt | cut -c1-200)"; done
echo "dup corpus ids: $(ls test-suite/corpus/pycsl-reference | grep -E '^[0-9]+_' | cut -d_ -f1 | sort | uniq -d | wc -l)"
git status --short src bin test-suite | head
echo "G3 end $(date -u) $(grep oom_kill $EV)"
