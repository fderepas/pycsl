#!/usr/bin/env bash
# Add loop invariants and loop variants to Python files that already have
# human-written contracts (#@ requires, #@ ensures, #@ assigns).
#
# This script NEVER generates contracts — it only infers in-function
# annotations (loop invariant, loop variant). No \trusted is ever added.
#
# Usage:
#   ./bin/infer-invariants-from-contract.sh <input.py>
#   ./bin/infer-invariants-from-contract.sh <input.py> --out <output.py>
#   ./bin/infer-invariants-from-contract --help
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

LOG_DIR="$PROJECT_ROOT/my_project/log"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <input.py>

Add #@ loop invariant and #@ loop variant annotations to every loop inside
functions that already have human-written contracts. Contracts themselves
(requires, ensures, assigns) are left untouched.

This script NEVER adds \\trusted and NEVER modifies requires/ensures/assigns.

Arguments:
  <input.py>          Python source file with existing #@ contracts

Options:
  --out <file>        Write annotated output to <file> (default: overwrite input)
  -h, --help          Show this help message

Log files:
  $LOG_DIR/agent-infer-invariants.log
      Per-function progress and any errors
  $LOG_DIR/agent-invariant-writer.log
      Raw LLM calls for loop invariant generation

Tip: watch progress with:
  tail -f $LOG_DIR/agent-infer-invariants.log
EOF
}

# Parse arguments
INPUT_FILE=""
OUTPUT_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --out)
            if [[ $# -lt 2 ]]; then
                echo "Error: --out requires a file argument" >&2
                exit 1
            fi
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -*)
            echo "Error: unknown option '$1'" >&2
            echo "Run '$(basename "$0") --help' for usage." >&2
            exit 1
            ;;
        *)
            if [[ -n "$INPUT_FILE" ]]; then
                echo "Error: multiple input files specified" >&2
                exit 1
            fi
            INPUT_FILE="$1"
            shift
            ;;
    esac
done

if [[ -z "$INPUT_FILE" ]]; then
    echo "Error: no input file specified" >&2
    echo "Run '$(basename "$0") --help' for usage." >&2
    exit 1
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: file not found: $INPUT_FILE" >&2
    exit 1
fi

if [[ -z "$OUTPUT_FILE" ]]; then
    OUTPUT_FILE="$INPUT_FILE"
fi

# Activate virtual environment
cd "$PROJECT_ROOT"
if [[ -f .venv/bin/activate ]]; then
    source .venv/bin/activate
else
    echo "Error: virtual environment not found at $PROJECT_ROOT/.venv" >&2
    exit 1
fi

mkdir -p "$LOG_DIR"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  PyCSL Invariant Inference                                  ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Input:  $INPUT_FILE"
echo "║  Output: $OUTPUT_FILE"
echo "║  Mode:   loop invariants/variants only (no contracts added)  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

AGENT_STDOUT_LOG="$LOG_DIR/agent-infer-invariants-stdout.log"
set +e
python src/pycsl/agents/agent-infer-invariants.py \
    --in "$INPUT_FILE" \
    --out "$OUTPUT_FILE" \
    > "$AGENT_STDOUT_LOG" 2>&1
RET_CODE=$?
set -e

echo ""
echo "────────────────────────────────────────────────────────────────"
if [[ $RET_CODE -eq 0 ]]; then
    echo "✓ Invariant inference complete: $OUTPUT_FILE"
    cat "$AGENT_STDOUT_LOG" 2>/dev/null || true
else
    echo "✗ Invariant inference failed (exit code $RET_CODE)"
    echo ""
    echo "Last 10 lines of agent output:"
    tail -10 "$AGENT_STDOUT_LOG" 2>/dev/null || true
fi
echo ""
echo "Log files for troubleshooting:"
echo "  Agent stdout:  $AGENT_STDOUT_LOG"
echo "  Invariants:    $LOG_DIR/agent-infer-invariants.log"
echo "  LLM calls:     $LOG_DIR/agent-invariant-writer.log"
echo "────────────────────────────────────────────────────────────────"

exit $RET_CODE
