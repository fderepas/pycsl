#!/usr/bin/env bash
# Yield over getting-better/open-routes/probes.tsv.
#   Yield denominator is LIVE + FAIL-CLOSED ONLY. VACUOUS rows are instrument failures
#   and are reported separately -- a probe whose positive control refused measured
#   nothing and must never count as a clean negative.
# Usage: bin/probe-ledger-yield.sh [--by-generator] [--by-generation] [--gen N] [--generator G]
set -euo pipefail
TSV="${TSV:-getting-better/open-routes/probes.tsv}"
MODE="${1:---summary}"; shift || true
FGEN=""; FGENR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --gen) FGEN="$2"; shift 2;;
    --generator) FGENR="$2"; shift 2;;
    *) shift;;
  esac
done
awk -F'\t' -v mode="$MODE" -v fgen="$FGEN" -v fgenr="$FGENR" '
  /^#/ {next} NF<8 {next} $5=="verdict" {next}
  fgen!="" && $2!=fgen {next}
  fgenr!="" && $3!=fgenr {next}
  {
    k = (mode=="--by-generator") ? $3 : (mode=="--by-generation") ? $2 : "ALL"
    if ($5=="LIVE")            { live[k]++; if($7=="2") second[k]++ }
    else if ($5=="FAIL-CLOSED"){ fc[k]++ }
    else if ($5=="VACUOUS")    { vac[k]++ }
    else                       { oth[k]++ }
    keys[k]=1
  }
  END{
    printf "%-20s %6s %6s %6s %8s %8s %8s\n","key","LIVE","FAILC","denom","yield","2nd-ord","VACUOUS"
    for (k in keys) {
      d = live[k]+fc[k]
      printf "%-20s %6d %6d %6d %8s %8d %8d\n", k, live[k], fc[k], d,
             (d>0 ? sprintf("%.1f%%", 100*live[k]/d) : "n/a"), second[k], vac[k]
    }
  }' "$TSV" | { read -r h; echo "$h"; sort; }
