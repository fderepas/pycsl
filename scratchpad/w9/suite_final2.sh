#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
timeout 28800 bash bin/run-reference-tests.sh --jobs 6 > scratchpad/w9/suite_final2.log 2>&1
echo $? > scratchpad/w9/suite_final2.rc
