#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
timeout 25200 bash bin/run-reference-tests.sh --jobs 3 > scratchpad/w9/suite_full.log 2>&1
echo $? > scratchpad/w9/suite_full.rc
