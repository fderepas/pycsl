#!/bin/bash
# G.sh : one NORMAL heavy job on the head snapshot tree pycsl-u74h (cwd = tree root): head sweep (bd+pyref+mirror),
# compares vs the base sweep (pycsl-u67b), the single-underscore mirror emission + 3 ledger slow planes, fidelity,
# fast planes teed in full, trusted count.
H=/home/fabrice/git/pycsl-u74h; S=/home/fabrice/git/pycsl-u74/scratchpad/u74/sw; G=/home/fabrice/git/pycsl-u74/scratchpad/u74/logs/G
mkdir -p $G $S/head; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "G start $(date -u) $(git -C $H log --oneline -1 | cut -c1-12) $(grep oom_kill $EV)"
cd $H || exit 2
bin/byte-diff-sweep.sh $S/head/bd > $S/head/bd.log 2>&1; echo "head bd rc=$? $(tail -2 $S/head/bd.log | tr '\n' ' ')"
bin/mirror-emit-sweep.sh $S/head/mir > $S/head/mir.log 2>&1; echo "head mir rc=$? $(tail -1 $S/head/mir.log)"
python3 bin/byte-diff-compare.py $S/base/bd $S/head/bd > $G/C-root.txt 2>&1; echo "compare root rc=$? $(tail -3 $G/C-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $S/base/bd/pyref $S/head/bd/pyref --min-files 2000 > $G/C-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -3 $G/C-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $S/base/mir $S/head/mir --min-files 45 > $G/C-mir.txt 2>&1; echo "compare mir rc=$? $(tail -3 $G/C-mir.txt | tr '\n' ' ')"
diff -rq $S/base/mir $S/head/mir > $G/diffrq-mir.txt 2>&1; echo "diff -rq mir rc=$? $(wc -l < $G/diffrq-mir.txt) lines"
E=$G/lg/mir_emit; mkdir -p $E
while IFS= read -r s; do rel="${s#"$H/src/self-annotate/src/"}"; n="${rel%.py}"; n="${n//\//_}"; rm -f "${s%.py}.mlw"
  PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py "$s" --import-path $H/src/pycsl --no-proof --keep-mlw --verification-image $H/src/self-annotate/src >/dev/null 2>&1
  [ -f "${s%.py}.mlw" ] && mv "${s%.py}.mlw" "$E/$n.mlw"; done < <(find $H/src/self-annotate/src -name '*.py' | sort)
echo "lg emitted $(ls $E | wc -l)"
for p in check-assigns-writes-survival check-trusted-frame-honesty; do python3 bin/$p.py --emit-dir $E > $G/lg/$p.txt 2>&1; echo "$p rc=$?"; done
python3 bin/check-getattr-erasure.py > $G/lg/check-getattr-erasure.txt 2>&1; echo "check-getattr-erasure rc=$?"
bash bin/check-self-annotate-sync.sh > $G/sync.txt 2>&1; echo "check-self-annotate-sync rc=$?"
bash bin/self-annotate-mirror-check.sh > $G/mircheck.txt 2>&1; echo "self-annotate-mirror-check rc=$?"
python3 bin/doc-coherency.py --check > $G/doccoh.txt 2>&1; echo "doc-coherency rc=$?"
bash bin/run-soundness-planes.sh 2>&1 | tee $G/planes.txt > /dev/null; echo "planes rc=${PIPESTATUS[0]} $(tail -3 $G/planes.txt | tr '\n' ' ')"
python3 bin/count-trusted-directives.py > $G/count-trusted.txt 2>&1; echo "count-trusted-directives rc=$? $(tail -2 $G/count-trusted.txt | tr '\n' ' ')"
echo "trusted (canonical grep) $(grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l)"
git -C $H diff --stat 96eac515d -- src/pycsl/proof_axiom_allowlist.py | tail -1; echo "allowlist diff lines: $(git -C $H diff 96eac515d -- src/pycsl/proof_axiom_allowlist.py | wc -l)"
git -C $H status --short src bin test-suite | head
echo "G end $(date -u) $(grep oom_kill $EV)"
