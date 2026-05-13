#!/bin/bash
set -e
set -x
SCRIPT_DIR=$(dirname $0)
cd $SCRIPT_DIR
cd ..
. .venv/bin/activate
for i in $(cd tests/to_annotate && ls *.py && cd ..) ; do
    echo $i
    OUT_STD=out.std
    OUT_ERR=out.err
    set +e
    python agents/agent-annotate.py --in tests/to_annotate/$i --out tests/annotated/$i > $OUT_STD 2> $OUT_ERR
    RET_CODE=$?
    set -e
    if [[ $RET_CODE -ne 0 ]]; then
        echo python agents/agent-reconcile.py --script tests/to_annotate/$i --stdout $OUT_STD --stderr $OUT_ERR --ret-code $RET_CODE
        exit 1
    fi
done

