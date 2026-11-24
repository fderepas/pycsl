#!/bin/bash
# ALL.sh : one NORMAL heavy job, sequential: v1f follow-up (J2), census rows (--append-new) + commit,
# base + head sweeps, compares, ledger/fidelity (LG), fast planes, rwc, corpus-executes.
W=/home/fabrice/git/pycsl-u64; B=/home/fabrice/git/pycsl-u64-base; G=$W/scratchpad/u64/logs/G; mkdir -p $G
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "ALL start $(date -u) $(grep oom_kill $EV)"
bash $W/scratchpad/u64/tools/J2.sh 2>&1 | sed 's/^/[J2] /'
cd $W
.venv/bin/python3 bin/check-refusal-witness-coverage.py --append-new > $G/census-append.txt 2>&1; echo "census append rc=$? $(tail -1 $G/census-append.txt)"
git diff --stat bin/refusal-witness-census.tsv
git add bin/refusal-witness-census.tsv && git commit -q -m "u64: census rows for witnesses 10340 / 10341 / 10343 (check-refusal-witness-coverage --append-new, _census_row)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"; echo "census commit $(git log --oneline -1)"
bash $W/scratchpad/u64/tools/S.sh $B $G/base 2>&1 | sed 's/^/[S-base] /'
bash $W/scratchpad/u64/tools/S.sh $W $G/head 2>&1 | sed 's/^/[S-head] /'
python3 bin/byte-diff-compare.py $G/base/bd $G/head/bd > $G/C-root.txt 2>&1; echo "compare root rc=$? $(tail -2 $G/C-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/bd/pyref $G/head/bd/pyref --min-files 2000 > $G/C-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -2 $G/C-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/mir $G/head/mir --min-files 45 > $G/C-mir.txt 2>&1; echo "compare mirror rc=$? $(tail -2 $G/C-mir.txt | tr '\n' ' ')"
diff -rq $G/base/mir $G/head/mir > $G/D-mir.txt 2>&1; echo "mirror diff -rq lines=$(wc -l < $G/D-mir.txt) files base=$(ls $G/base/mir/*.mlw | wc -l) head=$(ls $G/head/mir/*.mlw | wc -l)"
bash $W/scratchpad/u64/tools/LG.sh $G/lg 2>&1 | sed 's/^/[LG] /'
bash bin/run-soundness-planes.sh > $G/planes.txt 2>&1; echo "planes rc=$? $(tail -3 $G/planes.txt | tr '\n' ' ')"
python3 bin/check-refusal-witness-coverage.py > $G/rwc.txt 2>&1; echo "rwc rc=$? $(tail -2 $G/rwc.txt | tr '\n' ' ')"
python3 bin/check-corpus-executes.py --verbose > $G/ce.txt 2>&1; echo "corpus-executes rc=$? $(grep -E 'corpus-executes' $G/ce.txt | tail -2 | tr '\n' ' ')"
echo "ALL end $(date -u) $(grep oom_kill $EV)"
