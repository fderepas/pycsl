#!/bin/bash
# cache-test.sh <tree> <out> : the route #613 stdlib table is never trusted blindly. Reruns witness
# 10180 (refused) and control 10188 (emits) with the table (a) as built, (b) truncated, (c) of the
# wrong shape, (d) carrying another key (stale), (e) deleted; after each, the table must be rebuilt
# (valid JSON carrying the current key) and the verdicts unchanged.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
T=$1; O=$2; mkdir -p $O; cd $T || exit 2
run(){ for f in 10180_r613_json_local_re_false 10183_r613_json_local_nonstdlib_name_false 10188_r613_json_no_shadow_ctl; do
  fl=$(grep -m1 '^# pycsl-flags:' test-suite/corpus/pycsl-reference/$f.py | sed 's/^# pycsl-flags://')
  .venv/bin/python3 src/pycsl/pycsl.py --no-proof --no-typecheck $fl test-suite/corpus/pycsl-reference/$f.py > $O/$1-$f.log 2>&1
  echo "  $1 $f rc=$? $(grep -o "closure may load \`[a-z_]*\`" $O/$1-$f.log | head -1) $(grep -o 'Verification SUCCESS' $O/$1-$f.log)"
done; }
chk(){ C=$(ls src/pycsl/__pycache__/r613-stdlib-imports-*.json); python3 -I -c "
import json,sys; d=json.load(open('$C')); print('  table', '$C'.split('/')[-1], 'valid, key matches name:', d['key'][:40] in '$C', 'graph keys', len(d['graph']))"; }
echo "(a) as built"; run a; chk
C=$(ls src/pycsl/__pycache__/r613-stdlib-imports-*.json)
echo "(b) truncated to 20 bytes"; head -c 20 $C > $C.t && mv $C.t $C; wc -c < $C; run b; chk
echo "(c) wrong shape"; echo '{"key": "x", "graph": [1, 2]}' > $C; run c; chk
echo "(d) stale: right shape, another key, empty graph (would admit sitecustomize if trusted)"; echo '{"key": "0000", "graph": {}}' > $C; run d; chk
echo "(e) deleted"; rm -f "$C"; run e; chk
