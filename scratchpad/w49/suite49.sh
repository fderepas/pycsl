#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
bash bin/run-reference-tests.sh --jobs 3 > getting-better/proofs49/suite49_run1.log 2>&1
echo $? > getting-better/proofs49/suite49_run1.rc
echo "$(date -u +%H:%M) SUITE run1 rc=$(cat getting-better/proofs49/suite49_run1.rc)" >> getting-better/proofs49/queue49.progress
