#!/bin/bash
# Checks that non-#@ lines in src/pycsl/ match the rocq and lean self-annotate mirrors.
# Exit 1 if any divergence is found.

set -euo pipefail

MODULES=(
    Module1_Ingestor
    Module2_Parser
    Module3_Weaver
    Module4_SemanticAnalyzer
    Module5_IREmitter
    Module6_WhyMLTranspiler
    ConcurrencyChecker
    errors
    ir_schema
)

DIVERGED=0

for mod in "${MODULES[@]}"; do
    live="src/pycsl/${mod}.py"
    rocq="src/self-annotate/rocq/${mod}.py"
    lean="src/self-annotate/lean/${mod}.py"

    if [ ! -f "$live" ]; then
        continue
    fi

    for copy in "$rocq" "$lean"; do
        if [ ! -f "$copy" ]; then
            echo "MISSING: $copy"
            DIVERGED=1
            continue
        fi

        diff_out=$(diff <(grep -v '#@' "$live") <(grep -v '#@' "$copy") || true)
        if [ -n "$diff_out" ]; then
            echo "DIVERGED: $live vs $copy"
            echo "$diff_out" | head -40
            echo "---"
            DIVERGED=1
        fi
    done
done

if [ "$DIVERGED" -eq 0 ]; then
    echo "OK: all self-annotate mirrors are in sync"
fi

# resync-campaign.md R3.3: the module6_whyml/ subpackage mirror is heterogeneous (verbatim
# un-trusted handlers + intentionally-divergent trusted stubs), so a whole-file diff is
# meaningless — gate it with the method-level checker instead.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "--- module6_whyml/ mirror (method-level) ---"
if ! python3 "$SCRIPT_DIR/check-module6-mirror-sync.py"; then
    DIVERGED=1
fi

exit "$DIVERGED"
