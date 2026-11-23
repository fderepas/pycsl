#!/bin/bash
# run #9 2026-11-23 22:35Z: /tmp (shared tmpfs) is over user 1000's quota: all temp files go to the repo volume
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/run9/tmp
# camp.sh <tree> <tag> : one campaign RUNNER. Pops jobs from scratchpad/run9/<tag>-jobs.txt (flock) until empty.
# Job lines:  full <mirror-rel> <cpu>   |  main <mirror-rel> <cpu>   |  shard <mirror-rel> <k> <N> <cpu>
# full  = normal whole-file proof (main phase + vacuity gate);  main = --no-check-vacuity (main phase only);
# shard = vacshard.py k/N on the same file (vacuity probes i % N == k).  Results -> <tag>-results.txt
T=$1; TAG=$2; O=/home/fabrice/git/pycsl/scratchpad/run9; Q=$O/$TAG-jobs.txt; R=$O/$TAG-results.txt; OP=$(cat $O/oompath)
H=/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; cd $T
while true; do
  exec {q}>$Q.lock; flock $q; J=$(head -n 1 $Q); [ -n "$J" ] && sed -i 1d $Q; flock -u $q; exec {q}>&-
  [ -z "$J" ] && break
  # run #9 disk rule (2026-11-23 22:10Z): never launch with < 800 MB free on /tmp (shared tmpfs); wait and log
  while [ "$(df --output=avail -k /tmp | tail -n 1)" -lt 819200 ]; do echo "$(date -u +%FT%H:%MZ) DISK-WAIT /tmp avail $(df --output=avail -k /tmp | tail -n 1) kB before: $J" >> $O/$TAG-queue.txt; sleep 300; done
  set -- $J; kind=$1; f=$2; b=$(echo $f | tr / _); s=$(date +%s); o1=$(grep oom_kill $OP | awk '{print $2}')
  echo "$(date -u +%FT%H:%MZ) START $J" >> $O/$TAG-queue.txt
  case $kind in
    full|main) cpu=$3; L=$O/$TAG-$kind-$b.log; ex=""; [ $kind = main ] && ex="--no-check-vacuity"
      # statements.py / expressions.py main phases never overlap (run rule): serialise them on one lock
      BIGL=/dev/null; case $f in module6_whyml/statements.py|module6_whyml/expressions.py) BIGL=$O/bigmain.lock;; esac
      exec {bl}>$BIGL; [ "$BIGL" != /dev/null ] && flock $bl
      env HEAVY_SHORT=1 PYTHON_CPU_COUNT=$cpu $H .venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/$f --import-path src/pycsl --verification-image src/self-annotate/src $ex > $L 2>&1; rc=$?
      exec {bl}>&-
      res="valid=$(grep -c 'Prover result is: Valid' $L) total=$(grep -c 'Prover result is:' $L) $(grep -oE 'Verification (SUCCESS|FAILED)[^.!]*' $L | tail -1 | tr ' ' _)";;
    shard) k=$3; N=$4; cpu=$5; L=$O/$TAG-shard-$b-$k-of-$N.log
      env HEAVY_SHORT=1 PYTHON_CPU_COUNT=$cpu $H .venv/bin/python3 /home/fabrice/git/pycsl/scratchpad/run9/bin/vacshard.py $T $k $N src/self-annotate/src/$f --import-path src/pycsl --verification-image src/self-annotate/src > $L 2>&1; rc=$?
      res="$(grep -oE 'SHARD-RESULT .*' $L | cut -c1-200 | tr ' ' _) sha=$(grep -oE 'mlw sha256 [0-9a-f]{12}' $L | awk '{print $3}') probes=$(grep -oE 'probes [0-9]+' $L | head -1 | awk '{print $2}')";;
  esac
  o2=$(grep oom_kill $OP | awk '{print $2}')
  grep -q -E 'Disk quota exceeded|EDQUOT|No space left on device' $L && res="VOID-EDQUOT $res"
  echo "$kind $f ${k:+$k/$N} rc=$rc $res $(( $(date +%s)-s ))s oom $o1->$o2 tree=$(git rev-parse --short HEAD) $(/home/fabrice/git/pycsl/scratchpad/run9/bin/fp.sh $T)" >> $R
  unset k N
done
echo "$(date -u +%FT%H:%MZ) RUNNER-DONE $$" >> $O/$TAG-queue.txt
