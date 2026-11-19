#!/bin/bash
T=/home/fabrice/git/pycsl-lvW; O=$T/scratchpad/lvW/fidelity.log; cd $T; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
: > $O
bash bin/check-self-annotate-sync.sh >> $O 2>&1; echo "check-self-annotate-sync.sh rc=$?" >> $O
bash bin/self-annotate-mirror-check.sh >> $O 2>&1; echo "self-annotate-mirror-check.sh rc=$?" >> $O
python3 bin/doc-coherency.py --check >> $O 2>&1; echo "doc-coherency --check rc=$?" >> $O
