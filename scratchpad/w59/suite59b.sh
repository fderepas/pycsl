#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
bash bin/run-reference-tests.sh > getting-better/proofs49/suite59_run2.log 2>&1
echo $? > getting-better/proofs49/suite59_run2.rc
echo "$(date -u +%H:%M) finished suite59_run2 rc=$(cat getting-better/proofs49/suite59_run2.rc)" >> getting-better/proofs49/queue49.progress
