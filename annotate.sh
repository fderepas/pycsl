#!/bin/bash
# annotate.sh — Annotate a Python file with PyCSL contracts.
#
# Runs the annotation agent, then verifies with pycsl. On proof failure,
# runs agent-reconcile + agent-script-update and retries (up to MAX_RETRIES).
#
# Usage:
#   ./annotate.sh foo.py          # produces foo_annot.py
#   ./annotate.sh -i foo.py       # annotates in-place (overwrites foo.py)
#   ./annotate.sh -h              # show usage

set -e

PYCSL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$PYCSL_DIR/agents"
MAX_RETRIES=10

# ── usage ──────────────────────────────────────────────────────────────────────

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <file.py>

Annotate a Python file with PyCSL Design-by-Contract contracts.

The annotation agent adds Hoare-logic contracts (#@ requires, #@ ensures,
#@ assigns, etc.) to the input file, then verifies the result with pycsl.
If verification fails, a reconciliation/update loop retries up to
$MAX_RETRIES times.

Options:
  -i            Annotate in-place (overwrite the input file).
  -h, --help    Show this help message and exit.

Arguments:
  <file.py>     Path to the Python file to annotate.

Output:
  By default, <basename>_annot.py is created alongside the input file.
  With -i, the input file is overwritten with the annotated version.

Examples:
  $(basename "$0") toto.py        # creates toto_annot.py
  $(basename "$0") -i toto.py     # overwrites toto.py
  $(basename "$0") src/app.py     # creates src/app_annot.py
EOF
    exit 0
}

# ── parse arguments ────────────────────────────────────────────────────────────

INPLACE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -i)
            INPLACE=true
            shift
            ;;
        -*)
            echo "ERROR: Unknown option: $1" >&2
            echo "Try '$(basename "$0") --help' for more information." >&2
            exit 1
            ;;
        *)
            if [[ -n "${INPUT_FILE:-}" ]]; then
                echo "ERROR: Only one input file is allowed." >&2
                exit 1
            fi
            INPUT_FILE="$1"
            shift
            ;;
    esac
done

if [[ -z "${INPUT_FILE:-}" ]]; then
    echo "ERROR: No input file specified." >&2
    echo "Try '$(basename "$0") --help' for more information." >&2
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "ERROR: File not found: $INPUT_FILE" >&2
    exit 1
fi

# ── derived paths ──────────────────────────────────────────────────────────────

INPUT_FILE="$(cd "$(dirname "$INPUT_FILE")" && pwd)/$(basename "$INPUT_FILE")"
BASENAME="$(basename "$INPUT_FILE" .py)"
INPUT_DIR="$(dirname "$INPUT_FILE")"

if [[ "$INPLACE" == true ]]; then
    OUTPUT_FILE="$INPUT_FILE"
else
    OUTPUT_FILE="${INPUT_DIR}/${BASENAME}_annot.py"
fi

# Temporary working file for the annotation (always write here first)
WORK_FILE="${INPUT_DIR}/${BASENAME}_annot_tmp_$$.py"

# Temporary files for pycsl output
OUT_STD=$(mktemp)
OUT_ERR=$(mktemp)
RECONCILE_JSON=$(mktemp)
HISTORY_FILE=$(mktemp)
cleanup() {
    rm -f "$OUT_STD" "$OUT_ERR" "$RECONCILE_JSON" "$HISTORY_FILE" "$WORK_FILE"
}
trap cleanup EXIT

# ── activate venv ──────────────────────────────────────────────────────────────

if [[ -f "$PYCSL_DIR/.venv/bin/activate" ]]; then
    source "$PYCSL_DIR/.venv/bin/activate"
fi

# ── banner ─────────────────────────────────────────────────────────────────────

echo "================================================"
echo "PyCSL Annotation Script"
echo "================================================"
echo "Input:   $INPUT_FILE"
echo "Output:  $OUTPUT_FILE"
echo "Max retries: $MAX_RETRIES"
echo ""

# ── annotation + verification loop ─────────────────────────────────────────────

for attempt in $(seq 0 "$MAX_RETRIES"); do
    label="attempt $((attempt + 1))/$((MAX_RETRIES + 1))"

    # Step 1: Annotate
    echo "[annotate] $label — running annotation agent..."
    set +e
    python "$AGENTS_DIR/agent-annotate.py" \
        --in "$INPUT_FILE" \
        --out "$WORK_FILE" \
        > "$OUT_STD" 2> "$OUT_ERR"
    ANNOT_RC=$?
    set -e

    if [[ $ANNOT_RC -ne 0 ]]; then
        echo "[annotate] ERROR: Annotation agent failed (exit $ANNOT_RC)" >&2
        echo "--- stdout ---" >&2
        cat "$OUT_STD" >&2
        echo "--- stderr ---" >&2
        cat "$OUT_ERR" >&2
        exit 1
    fi

    # Step 2: Verify with pycsl
    echo "[annotate] $label — verifying with pycsl..."
    set +e
    python "$PYCSL_DIR/pycsl" --keep-mlw "$WORK_FILE" > "$OUT_STD" 2> "$OUT_ERR"
    PYCSL_RC=$?
    set -e

    if [[ $PYCSL_RC -eq 0 ]]; then
        echo "[annotate] ✓ Verification passed on $label"
        # Copy the working file to the final output
        if [[ "$INPLACE" == true ]]; then
            cp "$WORK_FILE" "$OUTPUT_FILE"
        else
            cp "$WORK_FILE" "$OUTPUT_FILE"
        fi
        echo "[annotate] ✓ Wrote $OUTPUT_FILE"
        exit 0
    fi

    echo "[annotate] ✗ Verification failed on $label"

    if [[ $attempt -eq $MAX_RETRIES ]]; then
        echo "[annotate] ERROR: Still failing after $MAX_RETRIES retries. Giving up." >&2
        exit 1
    fi

    # Step 3: Reconcile
    echo "[annotate] $label — running reconciliation agent..."
    set +e
    python "$AGENTS_DIR/agent-reconcile.py" \
        --script "$WORK_FILE" \
        --stdout "$OUT_STD" \
        --stderr "$OUT_ERR" \
        --ret-code "$PYCSL_RC" \
        --out "$RECONCILE_JSON"
    RECONCILE_RC=$?
    set -e

    if [[ $RECONCILE_RC -ne 0 ]]; then
        echo "[annotate] WARNING: Reconciliation failed (exit $RECONCILE_RC). Retrying annotation..." >&2
        continue
    fi

    # Step 4: Apply update
    echo "[annotate] $label — applying recommendations..."
    set +e
    python "$AGENTS_DIR/agent-script-update.py" \
        --recommendation "$RECONCILE_JSON" \
        --config "$AGENTS_DIR/agents-config.json" \
        --annotated-file "$WORK_FILE" \
        --history-file "$HISTORY_FILE"
    UPDATE_RC=$?
    set -e

    if [[ $UPDATE_RC -ne 0 ]]; then
        echo "[annotate] WARNING: Update agent failed (exit $UPDATE_RC). Retrying annotation..." >&2
        continue
    fi

    echo "[annotate] Recommendations applied. Re-verifying..."
done

echo "[annotate] ERROR: Exhausted all retries." >&2
exit 1
