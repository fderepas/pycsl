#!/usr/bin/env bash
# Compile all Rocq (.v) proof files with coqc and report results.
#
# Usage: ./bin/run-rocq-proofs.sh [directory]
#
# Default directory: to_be_proven/
# Searches recursively for .v files and compiles each with coqc.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default to to_be_proven/ if no directory given
PROOF_DIR="${1:-$PROJECT_ROOT/to_be_proven}"

# Find Why3 Coq library
WHY3_COQ_LIB=""
for candidate in \
    "$HOME/.opam/default/lib/why3/coq" \
    "$HOME/.opam/default/lib/coq/user-contrib/Why3"; do
    if [ -f "$candidate/BuiltIn.vo" ]; then
        WHY3_COQ_LIB="$candidate"
        break
    fi
done

if [ -z "$WHY3_COQ_LIB" ]; then
    # Try dynamic resolution
    if command -v opam &>/dev/null; then
        WHY3_LIB="$(opam var why3:lib 2>/dev/null || true)"
        if [ -n "$WHY3_LIB" ] && [ -f "$WHY3_LIB/coq/BuiltIn.vo" ]; then
            WHY3_COQ_LIB="$WHY3_LIB/coq"
        fi
    fi
fi

if [ -z "$WHY3_COQ_LIB" ]; then
    echo "ERROR: Could not find Why3 Coq library (BuiltIn.vo)."
    echo "Install with: opam install why3-coq"
    exit 1
fi

# Ensure coqc is on PATH
if ! command -v coqc &>/dev/null; then
    if [ -f "$HOME/.opam/default/bin/coqc" ]; then
        export PATH="$HOME/.opam/default/bin:$PATH"
    else
        echo "ERROR: coqc not found. Install Coq/Rocq."
        exit 1
    fi
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

echo "Rocq Proof Compilation Report"
echo "============================="
echo "Directory: $PROOF_DIR"
echo "Why3 Coq lib: $WHY3_COQ_LIB"
echo "coqc: $(command -v coqc) ($(coqc --version | head -1))"
echo ""

passed=0
failed=0
aborted=0
errors=()

# Find all .v files recursively
while IFS= read -r -d '' v_file; do
    name="$(basename "$v_file" .v)"
    rel_path="${v_file#$PROOF_DIR/}"

    # Check if file uses Abort (intentionally incomplete)
    if grep -q '\bAbort\b' "$v_file" 2>/dev/null; then
        echo -e "${YELLOW}[ABORT]${RESET} $rel_path (proof incomplete — needs manual completion)"
        ((aborted++))
        continue
    fi

    # Compile with coqc
    if output=$(coqc -R "$WHY3_COQ_LIB" Why3 "$v_file" 2>&1); then
        echo -e "${GREEN}[PASS]${RESET} $rel_path"
        ((passed++))
    else
        echo -e "${RED}[FAIL]${RESET} $rel_path"
        errors+=("$rel_path: $output")
        ((failed++))
    fi
done < <(find "$PROOF_DIR" -name "*.v" -print0 | sort -z)

total=$((passed + failed + aborted))

echo ""
echo "==============================="
echo -e " Results: ${GREEN}${passed}${RESET} passed, ${RED}${failed}${RESET} failed, ${YELLOW}${aborted}${RESET} aborted / ${total} total"
echo "==============================="

if [ ${#errors[@]} -gt 0 ]; then
    echo ""
    echo "Errors:"
    for err in "${errors[@]}"; do
        echo "  $err"
    done
fi

if [ "$failed" -gt 0 ]; then
    exit 1
fi
exit 0
