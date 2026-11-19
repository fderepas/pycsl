#!/bin/bash
# jobA.sh <head-tree> <out> : base json re-probes (x3, both bases), HEAD witness verdicts (x3),
# declared-run-mode tests, census rows for the FAIL witnesses, timing.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
T=$1; O=$2; mkdir -p $O
W=$T/witnesses-r613; PR=$T/witnesses-r613/pr-probes.sh
oom(){ grep oom_kill /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events; }
echo "start $(date -u) $(oom)" > $O/meta.txt
J="test-suite/corpus/pycsl-reference/10180_r613_json_local_re_false.py test-suite/corpus/pycsl-reference/10183_r613_json_local_nonstdlib_name_false.py test-suite/corpus/pycsl-reference/10184_r613_json_sourceless_re_pyc_false.py test-suite/corpus/pycsl-reference/10186_r613_json_namespace_dir_re_ctl.py test-suite/corpus/pycsl-reference/10187_r613_json_identical_codecs_copy_ctl.py test-suite/corpus/pycsl-reference/10188_r613_json_no_shadow_ctl.py"
for b in /home/fabrice/git/pycsl-u52-b899 /home/fabrice/git/pycsl-u52-b0057; do
  $PR $b $O/base-$(basename $b) $W/j0/prog.py $W/j1/prog.py $(for f in $J; do echo $b/$f; done) > /dev/null
done
$PR $T $O/head $W/j0/prog.py $W/j1/prog.py $W/h0/prog.py $W/h1/prog.py $W/n1/prog.py $W/s1/prog.py $T/test-suite/corpus/pycsl-reference/1018*_r613_*.py > /dev/null
cd $T
M=src/self-annotate/src
for f in $M/module6_whyml/scc.py $M/module6_whyml/types.py $M/module6_whyml/expressions.py; do
  for mode in script pkg; do
    fl=""; [ $mode = pkg ] && fl="--as-package-module $M"
    .venv/bin/python3 src/pycsl/pycsl.py --no-proof --no-typecheck --import-path src/pycsl $fl $f > $O/mode-$(basename $f .py)-$mode.log 2>&1
    echo "$f $mode rc=$? $(grep -m1 -A1 'PIPELINE ERROR' $O/mode-$(basename $f .py)-$mode.log | tail -1 | cut -c1-160) $(grep -m1 'Verification SUCCESS\|Declared run mode' $O/mode-$(basename $f .py)-$mode.log | cut -c1-100)" >> $O/modes.txt
  done
done
.venv/bin/python3 src/pycsl/pycsl.py --soundness-report --as-package-module $M --import-path src/pycsl $M/module6_whyml/scc.py > $O/sreport-pkg.log 2>&1; echo "sreport pkg rc=$?" >> $O/modes.txt
.venv/bin/python3 src/pycsl/pycsl.py --no-proof --no-typecheck --as-package-module src/pycsl $M/module6_whyml/scc.py > $O/mode-badroot.log 2>&1; echo "bad root rc=$? $(tail -1 $O/mode-badroot.log)" >> $O/modes.txt
# a stdlib-named module directly under ROOT still refuses under the declared mode
mkdir -p $O/pk/pkg && cp $W/j1/re.py $O/pk/re.py && touch $O/pk/pkg/__init__.py && cp $W/j0/prog.py $O/pk/pkg/prog.py
.venv/bin/python3 src/pycsl/pycsl.py --no-proof --no-typecheck --as-package-module $O/pk $O/pk/pkg/prog.py > $O/mode-pk.log 2>&1; echo "pk (re.py under ROOT) rc=$? $(grep -m1 -A1 'PIPELINE ERROR' $O/mode-pk.log | tail -1 | cut -c1-200)" >> $O/modes.txt
# census rows (the check's own writer), FAIL witnesses
.venv/bin/python3 scratchpad/u52/census.py $(ls test-suite/corpus/pycsl-reference/1018*_r613_*false.py) > $O/census-rows.tsv 2>$O/census.err
# timing (--no-proof --no-typecheck, 5 runs each)
for t in $T /home/fabrice/git/pycsl-u52-b899; do for k in 1 2 3 4 5; do
  /usr/bin/time -f "%e" -a -o $O/time-$(basename $t).txt .venv/bin/python3 $t/src/pycsl/pycsl.py --no-proof --no-typecheck test-suite/corpus/pycsl-reference/10188_r613_json_no_shadow_ctl.py >/dev/null 2>&1
done; done
echo "end $(date -u) $(oom)" >> $O/meta.txt
