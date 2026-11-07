#!/bin/bash
# cv5 phase-A census: runs AS the heavy.sh command (QUICK class via a trailing --no-proof arg).
# Port each strict-marker stub alone into the scratch tree, --no-proof type-check, restore.
S=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/cv5census
PY=/home/fabrice/git/pycsl/.venv/bin/python3
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
T=$S/tree; P=$S/pristine
cd "$T" || exit 2
n=0
grep -v '^#' /home/fabrice/git/pycsl-cv5/getting-better/trusted-reasons.tsv | tail -n +2 | while IFS=$'\t' read -r rel qn reason cite; do
  n=$((n+1)); id=$(printf '%03d' $n)
  [ -f "$S/logs/$id.done" ] && continue
  cp "$P/src/self-annotate/src/$rel" "$T/src/self-annotate/src/$rel"
  pm=$($PY "$T/bin/port-one-mirror-body.py" "$T" "$rel" "$qn" --convert 2>&1)
  if [[ "$pm" == ABORT*"not a facade"* ]]; then
    cp "$P/src/self-annotate/src/$rel" "$T/src/self-annotate/src/$rel"
    pm=$($PY "$T/bin/port-one-mirror-body.py" "$T" "$rel" "$qn" --convert --replace 2>&1)
  fi
  { echo "STUB	$rel	$qn	$reason"; echo "PORT	$pm"; } > "$S/logs/$id.log"
  if [[ "$pm" != ABORT* ]]; then
    t0=$(date +%s)
    timeout 1200 $PY src/pycsl/pycsl.py "src/self-annotate/src/$rel" --import-path "$T/src/pycsl" --no-proof >> "$S/logs/$id.log" 2>&1
    echo "RC	$?	$(( $(date +%s)-t0 ))s" >> "$S/logs/$id.log"
  fi
  cp "$P/src/self-annotate/src/$rel" "$T/src/self-annotate/src/$rel"
  touch "$S/logs/$id.done"
  echo "$(date -u +%FT%TZ) $id $rel $qn" >> "$S/progress.log"
done
echo "$(date -u +%FT%TZ) CENSUS-DONE" >> "$S/progress.log"
