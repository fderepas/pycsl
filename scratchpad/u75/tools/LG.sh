#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u75/scratchpad/u75/tmp; mkdir -p "$TMPDIR"
# LG.sh <outdir> : head mirror emission with the planes' single-underscore naming, then the three ledger slow
# planes individually (full output kept), count-trusted grep, fidelity scripts. cwd = u69 tree root.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
R=${LGT:-/home/fabrice/git/pycsl-u75}; O=$1; E=$O/mir_emit; mkdir -p $E; cd $R || exit 2
while IFS= read -r s; do rel="${s#"$R/src/self-annotate/src/"}"; n="${rel%.py}"; n="${n//\//_}"; rm -f "${s%.py}.mlw"
  PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py "$s" --import-path $R/src/pycsl --no-proof --keep-mlw --verification-image $R/src/self-annotate/src >/dev/null 2>&1
  [ -f "${s%.py}.mlw" ] && mv "${s%.py}.mlw" "$E/$n.mlw"; done < <(find $R/src/self-annotate/src -name '*.py' | sort)
echo "emitted $(ls $E | wc -l)"
for p in check-assigns-writes-survival check-trusted-frame-honesty; do python3 bin/$p.py --emit-dir $E > $O/$p.txt 2>&1; echo "$p rc=$?"; done
python3 bin/check-getattr-erasure.py > $O/check-getattr-erasure.txt 2>&1; echo "check-getattr-erasure rc=$?"
bash bin/check-self-annotate-sync.sh > $O/sync.txt 2>&1; echo "check-self-annotate-sync rc=$?"
bash bin/self-annotate-mirror-check.sh > $O/mircheck.txt 2>&1; echo "self-annotate-mirror-check rc=$?"
python3 bin/doc-coherency.py --check > $O/doccoh.txt 2>&1; echo "doc-coherency rc=$?"
echo "trusted $(grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l)"
git status --short src bin test-suite | head
