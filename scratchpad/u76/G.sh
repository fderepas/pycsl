#!/bin/bash
# G.sh: gates on the head snapshot tree pycsl-u76h (cwd = tree root): single-underscore mirror emission + ledger slow planes,
# check-assigns-underdeclaration, fidelity (sync / mircheck / doc-coherency / sibling + stdlib contract fidelity), fast planes teed, count-trusted.
H=/home/fabrice/git/pycsl-u76h; U=/home/fabrice/git/pycsl-u76/scratchpad/u76; G=$U/logs/G
mkdir -p $G; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=$U/tmp
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "G start $(date -u) $(git -C $H log --oneline -1 | cut -c1-12) $(grep oom_kill $EV)"
cd $H || exit 2
E=$G/lg/mir_emit; rm -rf "${G:?}/lg"; mkdir -p $E
while IFS= read -r s; do rel="${s#"$H/src/self-annotate/src/"}"; n="${rel%.py}"; n="${n//\//_}"; rm -f "${s%.py}.mlw"
  PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py "$s" --import-path $H/src/pycsl --no-proof --keep-mlw --verification-image $H/src/self-annotate/src >/dev/null 2>&1
  [ -f "${s%.py}.mlw" ] && mv "${s%.py}.mlw" "$E/$n.mlw"; done < <(find $H/src/self-annotate/src -name '*.py' | sort)
echo "lg emitted $(ls $E | wc -l)"
for p in check-assigns-writes-survival check-trusted-frame-honesty; do python3 bin/$p.py --emit-dir $E > $G/lg/$p.txt 2>&1; echo "$p rc=$? $(tail -1 $G/lg/$p.txt)"; done
python3 bin/check-getattr-erasure.py > $G/lg/check-getattr-erasure.txt 2>&1; echo "check-getattr-erasure rc=$? $(tail -1 $G/lg/check-getattr-erasure.txt)"
python3 bin/check-assigns-underdeclaration.py > $G/underdecl.txt 2>&1; echo "check-assigns-underdeclaration rc=$? $(tail -1 $G/underdecl.txt)"
bash bin/check-self-annotate-sync.sh > $G/sync.txt 2>&1; echo "check-self-annotate-sync rc=$?"
bash bin/self-annotate-mirror-check.sh > $G/mircheck.txt 2>&1; echo "self-annotate-mirror-check rc=$?"
python3 bin/doc-coherency.py --check > $G/doccoh.txt 2>&1; echo "doc-coherency rc=$?"
python3 bin/check-sibling-concrete-fidelity.py > $G/sibfid.txt 2>&1; echo "check-sibling-concrete-fidelity rc=$? $(tail -1 $G/sibfid.txt)"
python3 bin/check-stdlib-contract-fidelity.py > $G/stdfid.txt 2>&1; echo "check-stdlib-contract-fidelity rc=$? $(tail -1 $G/stdfid.txt)"
bash bin/run-soundness-planes.sh 2>&1 | tee $G/planes.txt > /dev/null; echo "planes rc=${PIPESTATUS[0]} $(tail -3 $G/planes.txt | tr '\n' ' ')"
python3 bin/count-trusted-directives.py > $G/count-trusted.txt 2>&1; echo "count-trusted-directives rc=$? $(tail -2 $G/count-trusted.txt | tr '\n' ' ')"
echo "trusted (canonical grep) $(grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l)"
echo "allowlist diff lines vs L21: $(git diff ba48d5888 -- src/pycsl/proof_axiom_allowlist.py | wc -l)"
echo "dup corpus ids: $(ls test-suite/corpus/pycsl-reference | grep -E '^[0-9]+_' | cut -d_ -f1 | sort | uniq -d | wc -l)"
git status --short src bin test-suite | head
echo "G end $(date -u) $(grep oom_kill $EV)"
