#!/bin/bash
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
cd /home/fabrice/git/pycsl-lvM/scratchpad/lvM/spike
why3 prove -P z3 -t 20 spike1.mlw 2>&1; echo "rc=$?"
why3 prove -P alt-ergo -t 20 spike1.mlw 2>&1; echo "rc=$?"

