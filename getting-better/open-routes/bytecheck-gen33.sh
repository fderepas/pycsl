#!/usr/bin/env bash
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
export PYTHONHASHSEED=0
cd /home/fabrice/git/pycsl || exit 9
S="$1"
echo "BYTECHECK START $(date -u +%FT%TZ) at $(git log --oneline -1)"
rm -rf /tmp/g33_after2
bash bin/byte-diff-sweep.sh /tmp/g33_after2 > "$S/bc_sweep.log" 2>&1
echo "sweep rc=$?"
python3 bin/byte-diff-compare.py /tmp/g33_before /tmp/g33_after2 \
    --new-source 1915_gen33_ctl_a_non_colliding_struct_pair_is_accepted.py \
                 1916_gen33_two_set_kappas_in_one_module.py \
                 1917_gen33_bare_dynamic_exec_in_a_function_rebinds_a_global.py \
                 1918_gen33_two_string_literals_concatenated.py \
                 1919_gen33_ctl_string_param_plus_literal.py \
    --expect-gone 0638 0639 \
    --expect-moved 1397_route136_bare_in_function_exec_and_constant_eval_still_prove \
    > "$S/bc_corpus.log" 2>&1
echo "corpus rc=$?"
python3 bin/byte-diff-compare.py /tmp/g33_before/pyref /tmp/g33_after2/pyref > "$S/bc_pyref.log" 2>&1
echo "pyref rc=$?"
echo "BYTECHECK END $(date -u +%FT%TZ)"
echo done > "$S/bc.rc"
