#!/usr/bin/env bash
# Phase C — bulk annotation runner.
# Iterates every stub under src/pycsl_lib/, skips ones already done
# in the pilot, per-module commit on success. No-stops-on-failure.
set -u
cd /home/fabrice.derepas@canonical.com/git/pycsl

# Pilot modules already done (Phase B + smoke)
declare -A PILOT
for m in keyword token string fractions math cmath statistics enum dataclasses decimal; do
    PILOT[$m]=1
done

# Collect every stub by stem (top-level + nested)
mapfile -t ALL_STUBS < <(find src/pycsl_lib -name '*.py' -not -path '*/__pycache__/*' \
                          -exec basename {} .py \; | sort -u | grep -v __init__)

TOTAL=${#ALL_STUBS[@]}
echo "Phase C bulk — $TOTAL stubs at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "============================================================="

ok_count=0
fail_count=0
skip_count=0
fail_list=()
n=0

for m in "${ALL_STUBS[@]}"; do
    n=$((n + 1))
    if [[ -n "${PILOT[$m]:-}" ]]; then
        skip_count=$((skip_count + 1))
        continue
    fi

    echo ""
    echo "--- [$n/$TOTAL] $m at $(date -u '+%H:%M:%SZ') ---"
    log="/tmp/phase-c-${m}.log"

    if bin/agent-stdlib-annotate --module "$m" > "$log" 2>&1; then
        verdict=$(grep -E 'VERDICT:|Outcome:|Δ L4\+' "$log" | tail -3 | tr '\n' ' ')
        echo "  $verdict"
        # Stage + commit any module-attributable changes
        if ! git diff --quiet -- "src/pycsl_lib/${m}.py" \
                "test-suite/corpus/python-reference/stdlib/${m}/" 2>/dev/null; then
            git add "src/pycsl_lib/${m}.py" \
                    "test-suite/corpus/python-reference/stdlib/${m}/" 2>/dev/null
            git commit -m "stdlib: annotate $m (Phase C)" > /dev/null 2>&1
            echo "  committed"
        fi
        ok_count=$((ok_count + 1))
    else
        rc=$?
        echo "  FAIL exit=$rc (see $log)"
        fail_list+=("$m")
        fail_count=$((fail_count + 1))
    fi
done

echo ""
echo "============================================================="
echo "Phase C bulk — done at $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo "OK:      $ok_count / $TOTAL"
echo "FAIL:    $fail_count / $TOTAL"
echo "SKIPPED: $skip_count / $TOTAL (pilot)"
if [[ $fail_count -gt 0 && $fail_count -le 30 ]]; then
    echo "Failing modules: ${fail_list[*]}"
fi
