#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
D=test-suite/corpus/pycsl-reference
for f in 1216_route85_dict_field_literal_modelled_empty 1217_route85_dict_field_contents_decided 1218_route85_set_field_literal_modelled_empty 1219_route85_dict_field_literal_now_faithful 1220_route86_map_param_coercion_substitutes_empty_map 1221_route86_empty_map_discharges_a_callee_requires; do
  exp=$(grep -q 'pycsl-expected: FAIL' $D/$f.py && echo FAILED || echo SUCCESS)
  printf "%-58s expect:%-8s " "${f:0:4}" "$exp"
  PYTHONHASHSEED=0 timeout 500 python3 src/pycsl/pycsl.py $D/$f.py --import-path src/pycsl 2>&1 | grep -oE 'SUCCESS|FAILED' | tail -1
done
