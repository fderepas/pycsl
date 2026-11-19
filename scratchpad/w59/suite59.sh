#!/bin/bash
# Reference suite run for route #80 — the ZERO-XPASS check.
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
bash bin/run-reference-tests.sh > getting-better/proofs49/suite59_run1.log 2>&1
echo $? > getting-better/proofs49/suite59_run1.rc
echo "$(date -u +%H:%M) finished suite59_run1 rc=$(cat getting-better/proofs49/suite59_run1.rc)" >> getting-better/proofs49/queue49.progress
