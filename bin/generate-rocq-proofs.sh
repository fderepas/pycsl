#!/usr/bin/env bash
# Generate Rocq proof companions for a PyCSL-annotated Python file.
#
# Usage:  bin/generate-rocq-proofs.sh <file.py>
#
# This script:
#   1. Runs pycsl to generate the .mlw file
#   2. Generates .v skeletons via Why3's Coq driver
#   3. Identifies which VCs failed SMT (postconditions)
#   4. Auto-fills the nia tactic (for polynomial arithmetic goals)
#   5. Compiles with coqc to verify
#   6. Creates a <file>.proofs/ directory with only the needed files
#
# Prerequisites:
#   - pycsl (in PATH or .venv)
#   - why3 with Coq prover installed (why3-coq)
#   - coqc (Rocq/Coq compiler)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Activate venv if available
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Find coqc
COQC="${COQC:-$(command -v coqc 2>/dev/null || echo "$HOME/.opam/default/bin/coqc")}"
WHY3_COQ="${WHY3_COQ:-$HOME/.opam/default/lib/why3/coq}"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <file.py>"
    echo ""
    echo "Generate Rocq proof companions for goals that SMT provers cannot discharge."
    exit 1
fi

INPUT="$1"
if [ ! -f "$INPUT" ]; then
    echo "[!] File not found: $INPUT"
    exit 1
fi

BASE="${INPUT%.py}"
PROOF_DIR="${BASE}.proofs"
MLW_FILE="${BASE}.mlw"

echo "[*] Step 1: Generating WhyML from $INPUT..."
pycsl --keep-mlw "$INPUT" 2>/dev/null || true

if [ ! -f "$MLW_FILE" ]; then
    echo "[!] Failed to generate .mlw file."
    exit 1
fi

echo "[*] Step 2: Creating proof directory $PROOF_DIR/"
mkdir -p "$PROOF_DIR"
cp "$MLW_FILE" "$PROOF_DIR/"

echo "[*] Step 3: Generating .v skeletons via Why3 Coq driver..."
ORIGDIR="$(pwd)"
cd "$(dirname "$MLW_FILE")"
MLW_BASE="$(basename "$MLW_FILE")"
why3 prove -P "Coq,8.20.1," -a split_vc -o "$(basename "$PROOF_DIR")" "$MLW_BASE" 2>/dev/null || true
cd "$ORIGDIR"

# Rename .v files that start with a digit (Rocq requires valid identifiers)
for vfile in "$PROOF_DIR"/*.v; do
    [ -f "$vfile" ] || continue
    fname="$(basename "$vfile")"
    if [[ "$fname" =~ ^[0-9] ]]; then
        mv "$vfile" "$PROOF_DIR/proof_${fname#*_}"
    fi
done

V_COUNT=$(ls "$PROOF_DIR"/*.v 2>/dev/null | wc -l)
echo "    Generated $V_COUNT .v files"

echo "[*] Step 4: Identifying postcondition VCs and filling nia proofs..."
FILLED=0
for vfile in "$PROOF_DIR"/*.v; do
    [ -f "$vfile" ] || continue
    # Postcondition VCs contain the loop exit condition
    if grep -q '~ (i < n)' "$vfile" 2>/dev/null; then
        # Check how many loop invariant axioms to determine accumulator count
        INVARIANT_COUNT=$(grep -c 'Axiom LoopInvariant' "$vfile" 2>/dev/null || echo 0)

        # Build pose proof lines based on invariant count
        POSE_LINES="  pose proof LoopInvariant as Ha."
        if [ "$INVARIANT_COUNT" -ge 2 ]; then
            POSE_LINES="$POSE_LINES\n  pose proof LoopInvariant1 as Hb."
        fi
        if [ "$INVARIANT_COUNT" -ge 3 ]; then
            POSE_LINES="$POSE_LINES\n  pose proof LoopInvariant2 as Hc."
        fi
        if [ "$INVARIANT_COUNT" -ge 4 ]; then
            POSE_LINES="$POSE_LINES\n  pose proof LoopInvariant3 as Hd."
        fi

        # Add Lia import and fill proof
        python3 -c "
import sys
with open('$vfile') as f:
    content = f.read()

if 'Require Import ZArith Lia.' not in content:
    content = content.replace(
        'Require int.EuclideanDivision.',
        'Require int.EuclideanDivision.\nRequire Import ZArith Lia.'
    )

proof = '''$(echo -e "$POSE_LINES")
  pose proof H as Hi0. pose proof H1 as Hi1. pose proof H2 as Hi2.
  assert (i = n) by lia. subst.
  nia.'''

content = content.replace('Proof.\n\n\nQed.', 'Proof.\n' + proof + '\nQed.')
with open('$vfile', 'w') as f:
    f.write(content)
"
        echo "    Filled proof in $(basename "$vfile")"
        FILLED=$((FILLED + 1))
    fi
done

if [ "$FILLED" -eq 0 ]; then
    echo "    No postcondition VCs found — proofs may need manual completion."
fi

echo "[*] Step 5: Compiling proofs with coqc..."
COMPILED=0
COMPILE_FAILED=0
for vfile in "$PROOF_DIR"/*.v; do
    [ -f "$vfile" ] || continue
    # Only compile postcondition proofs (the ones we filled)
    if grep -q 'nia\.' "$vfile" 2>/dev/null; then
        if "$COQC" -R "$WHY3_COQ" Why3 "$vfile" 2>/dev/null; then
            echo "    ✅ $(basename "$vfile")"
            COMPILED=$((COMPILED + 1))
        else
            echo "    ❌ $(basename "$vfile") — coqc failed"
            COMPILE_FAILED=$((COMPILE_FAILED + 1))
        fi
    fi
done

# Clean up: remove trivial VCs (keep only postcondition proofs + .mlw)
echo "[*] Step 6: Cleaning up trivial VCs..."
for vfile in "$PROOF_DIR"/*.v; do
    [ -f "$vfile" ] || continue
    if ! grep -q 'nia\.' "$vfile" 2>/dev/null; then
        rm "$vfile"
    fi
done
rm -f "$PROOF_DIR"/*.vo "$PROOF_DIR"/*.vok "$PROOF_DIR"/*.vos "$PROOF_DIR"/*.glob

FINAL_COUNT=$(ls "$PROOF_DIR"/*.v 2>/dev/null | wc -l)

echo ""
echo "==============================="
echo " Proof generation complete"
echo " Directory: $PROOF_DIR/"
echo " Proofs:    $FINAL_COUNT .v file(s)"
echo " Compiled:  $COMPILED OK, $COMPILE_FAILED failed"
echo "==============================="
echo ""
echo "To verify: pycsl $INPUT"

# Clean up generated .mlw in source dir
rm -f "$MLW_FILE"
