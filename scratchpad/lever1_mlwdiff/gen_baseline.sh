#!/bin/bash
set -e
cd /home/fabrice.derepas@canonical.com/git/pycsl
S=scratchpad/lever1_mlwdiff
FILES="src/pycsl/module6_whyml/expressions.py src/pycsl/module6_whyml/functions.py src/pycsl/module6_whyml/statements.py src/pycsl/module6_whyml/stmt_control_flow.py src/pycsl/module6_whyml/types.py src/self-annotate/src/module6_whyml/stmt_control_flow.py"
# 1. revert my 5 files to HEAD (non-destructive: originals saved in $S/save)
for f in $FILES; do git show HEAD:$f > $f; done
echo "reverted to HEAD"
# 2. baseline manifest
bash $S/gen_manifest.sh $S/baseline.md5
# 3. restore my versions
for f in $FILES; do cp $S/save/$f $f; done
echo "restored build versions"
echo BASELINE_DONE > $S/baseline.done
