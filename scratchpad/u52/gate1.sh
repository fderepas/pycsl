#!/bin/bash
# gate1.sh <snapshot-tree> <outdir> : corpus root + pyref sweep, mirror sweep, compares vs the L15
# emission (v66 bd-int / mir-int), and the static root scan. cwd = the tree root (rule 28).
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
T=$1; O=$2; mkdir -p $O; S=$O/summary.txt
V=/home/fabrice/git/pycsl/scratchpad/run8/v66
log(){ echo "$(date -u +%H:%MZ) $*" | tee -a $S; }
cd $T || exit 2
log "start tree $(git -C $T rev-parse --short HEAD)"
python3 -I $T/witnesses-r613/scan-roots.py $T > $O/scan.txt 2>&1; log "scan rc=$?"
bin/byte-diff-sweep.sh $O/bd > $O/bd.log 2>&1; log "sweep rc=$?: $(tail -2 $O/bd.log | tr '\n' ' ')"
NS=$(cd $T && ls test-suite/corpus/pycsl-reference/1018[0-9]_r613_*.py | xargs -n1 basename | sed 's/\.py$//')
python3 bin/byte-diff-compare.py $V/bd-int $O/bd --new-source $NS > $O/C-root.txt 2>&1; log "C root rc=$?: $(tail -3 $O/C-root.txt | tr '\n' ' ' | cut -c1-400)"
python3 bin/byte-diff-compare.py $V/bd-int/pyref $O/bd/pyref --min-files 2000 > $O/C-pyref.txt 2>&1; log "C pyref rc=$?: $(tail -3 $O/C-pyref.txt | tr '\n' ' ' | cut -c1-400)"
bin/mirror-emit-sweep.sh $O/mir > $O/mir.log 2>&1; log "mirror sweep rc=$?: $(tail -1 $O/mir.log)"
diff -rq $V/mir-int/ $O/mir/ > $O/D.txt 2>&1; log "D mirror: $(ls $O/mir | grep -c mlw) emitted, diff lines $(wc -l < $O/D.txt)"
log "GATE1-DONE"
