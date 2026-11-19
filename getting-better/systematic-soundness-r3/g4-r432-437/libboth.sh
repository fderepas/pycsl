#!/bin/bash
# libboth.sh --no-proof : pycsl_lib refusal screen (no typecheck) at base and candidate. Run AS heavy.sh (QUICK).
G=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/g4
find /home/fabrice/git/pycsl-g4-base/src/pycsl_lib -name '*.py' | sort > $G/lib-base.txt
find /home/fabrice/git/pycsl-g4/src/pycsl_lib -name '*.py' | sort > $G/lib-cand.txt
$G/codescr.sh /home/fabrice/git/pycsl-g4-base $G/lib-base.tsv $G/lib-base.txt
$G/codescr.sh /home/fabrice/git/pycsl-g4 $G/lib-cand.tsv $G/lib-cand.txt
echo LIBDONE
