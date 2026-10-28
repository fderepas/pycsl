#!/bin/bash
# h442 gate battery part 2 (census rows, planes, ledger checks, lib screen, witnesses). Run AS ONE heavy.sh job.
H=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/h442
W=/home/fabrice/git/pycsl-h442; B=/home/fabrice/git/pycsl-h442-base
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
L=$H/gates; mkdir -p $L
cd $W
echo "part2 start $(date -u +%FT%TZ)" >> $L/rc.txt
CENSUS=1; REMEASURE="4812_gen37_r358_object_attr_noexc.py 4813_gen37_r358_any_attr_noexc.py 4825_gen37_r358_any_result_attr_noexc.py 4765_gen37_r356_members_values_loop.py 4766_gen37_r356_value2member_map_loop.py 5013_gen37_r370_partial_value.py 5018_gen37_r370_partial_by_value.py"
if [ -n "$CENSUS" ]; then
  .venv/bin/python3 getting-better/systematic-soundness-r3/h442-r442-443/census.py $W $REMEASURE > $L/census.log 2>&1; echo "census rc=$?" >> $L/rc.txt
fi
bash bin/run-soundness-planes.sh > $L/planes.log 2>&1; echo "planes rc=$? $(date -u +%FT%TZ)" >> $L/rc.txt
python3 bin/check-trusted-reasons.py > $L/trusted-reasons.log 2>&1; echo "trusted-reasons rc=$?" >> $L/rc.txt
python3 bin/doc-coherency.py --check > $L/doc.log 2>&1; echo "doc rc=$?" >> $L/rc.txt
python3 bin/check-assumed-facts.py --emit-dir $H/ca > $L/assumed.log 2>&1; echo "assumed rc=$?" >> $L/rc.txt
python3 bin/check-clause-survival.py --emit-dir $H/ca > $L/clause.log 2>&1; echo "clause rc=$?" >> $L/rc.txt
for c in check-refusal-witness-coverage check-refusal-advice-audited check-dropped-mutation check-getattr-erasure check-open-route-carriers check-trusted-frame-honesty check-trusted-raises-honesty check-stdlib-modules-verify; do
  .venv/bin/python3 bin/$c.py > $L/$c.log 2>&1; echo "$c rc=$?" >> $L/rc.txt; done
echo "trusted $(grep -rhF '#@ \trusted' src/self-annotate/src --include=*.py | wc -l)" >> $L/rc.txt
find $B/src/pycsl_lib -name '*.py' | sort > $H/lib-base.txt; find $W/src/pycsl_lib -name '*.py' | sort > $H/lib-cand.txt
$H/codescr.sh $B $H/lib-base.tsv $H/lib-base.txt > /dev/null; $H/codescr.sh $W $H/lib-cand.tsv $H/lib-cand.txt > /dev/null
sed 's#/home/fabrice/git/pycsl-h442-base/#/W/#g' $H/lib-base.tsv > $H/lib-base.n; sed 's#/home/fabrice/git/pycsl-h442/#/W/#g' $H/lib-cand.tsv > $H/lib-cand.n
cmp -s $H/lib-base.n $H/lib-cand.n; echo "lib-screen identical rc=$? ($(wc -l < $H/lib-cand.n) files)" >> $L/rc.txt
rm -rf "${H:?}/fw"
$H/scr.sh $W $H/fw --full 3 $(cat $H/full-cand.txt) > /dev/null; echo "witnesses-final done" >> $L/rc.txt
echo "G2MAIN $(date -u +%FT%TZ)" >> $L/rc.txt
M1="3289_gen37_dvw_hval_doubled_get_nonmap_noexc_false_claim.py 4812_gen37_r358_object_attr_noexc.py 4813_gen37_r358_any_attr_noexc.py 4825_gen37_r358_any_result_attr_noexc.py 4765_gen37_r356_members_values_loop.py 4766_gen37_r356_value2member_map_loop.py 5013_gen37_r370_partial_value.py 5018_gen37_r370_partial_by_value.py"
rm -rf "${H:?}/m1b" "${H:?}/m1c"
$H/scr.sh $B $H/m1b --full 3 $(for f in $M1; do echo $B/test-suite/corpus/pycsl-reference/$f; done) > /dev/null
$H/scr.sh $W $H/m1c --full 3 $(for f in $M1; do echo $W/test-suite/corpus/pycsl-reference/$f; done) > /dev/null
echo "M1DONE $(date -u +%FT%TZ)" >> $L/rc.txt
echo "GATESDONE $(date -u +%FT%TZ)" >> $L/rc.txt
