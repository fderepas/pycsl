#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
bash bin/run-reference-tests.sh --jobs 6 > getting-better/proofs46/suite_final4.log 2>&1
echo $? > getting-better/proofs46/suite_final4.rc
