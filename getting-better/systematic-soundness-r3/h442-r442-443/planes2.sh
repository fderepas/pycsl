#!/bin/bash
H=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/h442
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
cd /home/fabrice/git/pycsl-h442; L=$H/gates-final
bash bin/run-soundness-planes.sh > $L/planes.log 2>&1; echo "planes rc=$? $(date -u +%FT%TZ)" >> $L/rc.txt
python3 bin/check-clause-survival.py --emit-dir $H/ca2 > $L/clause.log 2>&1; echo "clause rc=$?" >> $L/rc.txt
python3 bin/check-assumed-facts.py --emit-dir $H/ca2 > $L/assumed.log 2>&1; echo "assumed rc=$?" >> $L/rc.txt
for c in check-getattr-erasure check-open-route-carriers check-dropped-mutation check-trusted-frame-honesty check-trusted-raises-honesty check-trusted-reasons; do .venv/bin/python3 bin/$c.py > $L/$c.log 2>&1; echo "$c rc=$?" >> $L/rc.txt; done
echo "PLANES2DONE $(date -u +%FT%TZ)" >> $L/rc.txt
