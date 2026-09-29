#!/usr/bin/env bash
# gen #33 full battery for route #228. FOREGROUND of its own detached shell, one leg at a
# time, every leg TEE'd IN FULL (lesson d4 — never tail a leg you will be asked to quote).
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
export PYTHONHASHSEED=0
cd /home/fabrice/git/pycsl || exit 9
S="$1"
echo "BATTERY START $(date -u +%FT%TZ) at $(git log --oneline -1)"

echo "=== LEG 1: soundness planes --slow ==="
bash bin/run-soundness-planes.sh --slow > "$S/leg1_planes.log" 2>&1
echo "LEG1 rc=$?"

echo "=== LEG 2: byte-diff baseline worktree at HEAD ==="
rm -rf /home/fabrice/git/pycsl-g33wt /tmp/g33_before /tmp/g33_after
git worktree add --detach /home/fabrice/git/pycsl-g33wt 0375dec1 > "$S/leg2_wt.log" 2>&1
ln -s /home/fabrice/git/pycsl/.venv /home/fabrice/git/pycsl-g33wt/.venv
( cd /home/fabrice/git/pycsl-g33wt && bash bin/byte-diff-sweep.sh /tmp/g33_before ) > "$S/leg2_before.log" 2>&1
echo "LEG2-before rc=$?"
bash bin/byte-diff-sweep.sh /tmp/g33_after > "$S/leg2_after.log" 2>&1
echo "LEG2-after rc=$?"
echo "--- pycsl corpus comparison ---"
python3 bin/byte-diff-compare.py /tmp/g33_before /tmp/g33_after \
    --new-source 1915_gen33_ctl_a_non_colliding_struct_pair_is_accepted.py \
                 1916_gen33_two_set_kappas_in_one_module.py \
                 1917_gen33_bare_dynamic_exec_in_a_function_rebinds_a_global.py \
                 1918_gen33_two_string_literals_concatenated.py \
                 1919_gen33_ctl_string_param_plus_literal.py \
    --expect-gone 0638 0639 \
    --expect-moved 1397_route136_bare_in_function_exec_and_constant_eval_still_prove \
    > "$S/leg2_cmp_corpus.log" 2>&1
echo "LEG2-cmp-corpus rc=$?"
echo "--- python-reference comparison (lesson c4: TWICE, once per emitted tree) ---"
python3 bin/byte-diff-compare.py /tmp/g33_before/pyref /tmp/g33_after/pyref > "$S/leg2_cmp_pyref.log" 2>&1
echo "LEG2-cmp-pyref rc=$?"

echo "=== LEG 3: reference suite ==="
bash bin/run-reference-tests.sh > "$S/leg3_suite.log" 2>&1
echo "LEG3 rc=$?"

echo "BATTERY END $(date -u +%FT%TZ)"
echo "done" > "$S/battery.rc"
