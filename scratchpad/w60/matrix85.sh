#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
run(){ printf "%-34s %-10s " "$1" "$2"; PYTHONHASHSEED=0 timeout 500 python3 src/pycsl/pycsl.py "$3" --import-path src/pycsl 2>&1 | grep -oE 'SUCCESS|FAILED' | tail -1; }
echo "### ROUTE 85 CARRIERS — must REFUSE ###"
run membership        expect:FAILED scratchpad/w60/c5/b_direct.py
run contents          expect:FAILED scratchpad/w60/r85/c2_valueread.py
run set_field         expect:FAILED scratchpad/w60/r85/c5_setfield.py
run cross_call        expect:FAILED scratchpad/w60/r85/c4_discharges_requires.py
echo "### ROUTE 85 TRUE TWIN — must PROVE (completeness gain) ###"
run true_twin         expect:SUCCESS scratchpad/w60/c5/b_twin.py
echo "### ROUTE 86 CARRIERS — must REFUSE ###"
run r86_value         expect:FAILED scratchpad/w60/r86/v1_value.py
run r86_twin          expect:FAILED scratchpad/w60/r86/v1_twin.py
echo "### CONTROLS — must be UNCHANGED ###"
run ctl_empty_dict    expect:SUCCESS scratchpad/w60/r85/ctl_empty.py
run ctl_param_dict    expect:FAILED scratchpad/w60/r85/c6_param_dict.py
run ctl_list_field    expect:FAILED scratchpad/w60/r85/c3_listfield.py
echo "### ROUTE 79/83 CONTROLS — must still PROVE ###"
run r79_bounding      expect:SUCCESS test-suite/corpus/pycsl-reference/1215_route79_capture_and_defaults_still_faithful.py
run r83_bounding      expect:SUCCESS test-suite/corpus/pycsl-reference/1211_route83_straight_line_init_still_faithful.py
