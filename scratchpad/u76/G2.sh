#!/bin/bash
# G2.sh: after dropping the vacuous `#@ requires True` lines from the new corpus files: real census rows of the edited FAIL witnesses (worktree),
# commit, move the head snapshot, re-run the witness proofs there, claim-vacuity, and the full fast planes (teed).
U=/home/fabrice/git/pycsl-u76/scratchpad/u76; W=/home/fabrice/git/pycsl-u76; H=/home/fabrice/git/pycsl-u76h; G=$U/logs/G2; mkdir -p $G
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=$U/tmp
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "G2 start $(date -u) $(grep oom_kill $EV)"
cd $W || exit 2; C=test-suite/corpus/pycsl-reference
.venv/bin/python3 $U/cen_rows.py $(ls $PWD/$C/1051[0-5]_*.py $PWD/$C/10521_*.py) > $G/cen.txt 2>&1; echo "cen rc=$? $(wc -l < $G/cen.txt) rows"
git add bin/refusal-witness-census.tsv $C/1051[0-5]_*.py $C/10521_*.py $C/zu76a.py $C/zu76b.py $C/zu76n.py && git commit -q -m "u76: drop the vacuous \`#@ requires True\` from the new corpus files (claim-vacuity ratchet 1131); census rows re-measured with the real _census_row

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"; echo "commit $(git log --oneline -1 | cut -c1-12)"
git -C $H checkout -q --detach $(git rev-parse HEAD); echo "head snapshot $(git -C $H log --oneline -1 | cut -c1-12)"
$U/pw.sh $H > $G/wit.txt 2>&1; echo "witnesses: $(grep -c . $G/wit.txt) lines"; cat $G/wit.txt | grep -v "^All contracts"
cd $H || exit 2
python3 bin/check-claim-vacuity.py > $G/claim-vacuity.txt 2>&1; echo "check-claim-vacuity rc=$? $(tail -1 $G/claim-vacuity.txt)"
bash bin/run-soundness-planes.sh 2>&1 | tee $G/planes.txt > /dev/null; echo "planes rc=${PIPESTATUS[0]} $(tail -3 $G/planes.txt | tr '\n' ' ')"
echo "G2 end $(date -u) $(grep oom_kill $EV)"
