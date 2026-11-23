#!/bin/bash
# FINAL.sh : one NORMAL heavy job after the head2 sweep: census row for the refusal witness 10362 (real
# _census_row, appended + committed), type-only census of the witness emissions, sweep compares, then G.sh.
W=/home/fabrice/git/pycsl-u65; S=$W/scratchpad/u65/sw; G=$W/scratchpad/u65/logs/G; mkdir -p $G
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
cd $W || exit 2
grep -q "^bd rc=0" $S/head2/done.txt && grep -q "^mir rc=0" $S/head2/done.txt || { echo "head2 sweep not complete"; exit 3; }
.venv/bin/python3 scratchpad/u65/tools/CR.py $G/CR-rows.tsv test-suite/corpus/pycsl-reference/10362_r620_method_toplevel_whyml_name_clash_false.py; echo "CR rc=$? $(cut -c1-160 $G/CR-rows.tsv)"
if grep -q "^10362_.*	REFUSAL	.*PYCSL-SEM-WHYML-NAME-CLASH" $G/CR-rows.tsv && ! grep -q "^10362_" bin/refusal-witness-census.tsv; then
  cat $G/CR-rows.tsv >> bin/refusal-witness-census.tsv
  git add bin/refusal-witness-census.tsv && git commit -q -m "u65: census row for refusal witness 10362 (the real _census_row of check-refusal-witness-coverage, cwd = tree root, relative path)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"; echo "census commit $(git log --oneline -1 | cut -c1-12)"
fi
ls $S/head2/bd/1036[0-4]_*.mlw > $G/wit-mlw.txt
.venv/bin/python scratchpad/u65/tools/pfcensus.py $W $G/wit-census.tsv $(cat $G/wit-mlw.txt) > $G/wit-census.log 2>&1; echo "witness census: $(tr '\n' ' ' < $G/wit-census.log)"
python3 bin/byte-diff-compare.py $S/base/bd $S/head2/bd > $G/C-root.txt 2>&1; echo "compare root rc=$? $(tail -2 $G/C-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $S/base/bd/pyref $S/head2/bd/pyref --min-files 2000 > $G/C-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -2 $G/C-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $S/base/mir $S/head2/mir --min-files 45 > $G/C-mir.txt 2>&1; echo "compare mirror rc=$? $(tail -2 $G/C-mir.txt | tr '\n' ' ')"
diff -rq $S/base/mir $S/head2/mir > $G/D-mir.txt 2>&1; echo "mirror diff -rq lines=$(wc -l < $G/D-mir.txt) files base=$(ls $S/base/mir/*.mlw | wc -l) head=$(ls $S/head2/mir/*.mlw | wc -l)"
bash $W/scratchpad/u65/tools/G.sh
