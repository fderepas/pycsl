#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
f="$1"; tag="$2"
PYTHONHASHSEED=0 timeout 39600 python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl \
  > getting-better/proofs46/$tag.log 2>&1
echo $? > getting-better/proofs46/$tag.rc
