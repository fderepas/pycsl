#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
P=getting-better/proofs49
echo "$(date -u +%H:%M) started suite60_run1 (route #83 gate; sole suite, /tmp at 10%)" >> $P/queue49.progress
bash bin/run-reference-tests.sh > $P/suite60_run1.log 2>&1
echo $? > $P/suite60_run1.rc
echo "$(date -u +%H:%M) finished suite60_run1 rc=$(cat $P/suite60_run1.rc)" >> $P/queue49.progress
