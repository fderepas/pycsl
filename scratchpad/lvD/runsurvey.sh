#!/bin/bash
# runsurvey.sh <list> <outdir> : one heavy.sh QUICK call per stub
L=/home/fabrice/git/pycsl-lvD/scratchpad/lvD; out=$2; mkdir -p $out
while IFS=$'\t' read rel fn; do
  echo "$(date -u) lvD survey $fn ($out)" >> /home/fabrice/git/pycsl-lvD/progress.txt
  /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh $L/survey.sh "$rel" "$fn" $out --no-proof < /dev/null
done < $1
echo DONE > $out/done
