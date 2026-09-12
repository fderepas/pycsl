#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
bash bin/run-reference-tests.sh > getting-better/proofs49/suite59_run3.log 2>&1
echo $? > getting-better/proofs49/suite59_run3.rc
echo "$(date -u +%H:%M) finished suite59_run3 rc=$(cat getting-better/proofs49/suite59_run3.rc)" >> getting-better/proofs49/queue49.progress
