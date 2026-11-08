#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
bash bin/run-reference-tests.sh --pycsl --jobs 6 > scratchpad/w6/suite_pycsl.log 2>&1
echo "rc=$? suite_pycsl" >> scratchpad/w6/proofs/RC.txt
