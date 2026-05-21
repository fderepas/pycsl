#!/usr/bin/env bash
# Annotate a Python file with formal verification contracts using the PyCSL
# multi-agent LLM pipeline.
#
# Usage:
#   ./bin/annotate.sh <input.py>                  # annotate in-place
#   ./bin/annotate.sh <input.py> --out <output.py> # write to separate file
#   ./bin/annotate.sh --help
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Log directory (matches config/agents-config.json → project-directory)
LOG_DIR="$PROJECT_ROOT/my_project/log"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <input.py>

Annotate a Python file with formal verification contracts (requires, ensures,
assigns, loop invariants, loop variants) using the PyCSL multi-agent pipeline.

Arguments:
  <input.py>          Python source file to annotate

Options:
  --out <file>        Write annotated output to <file> (default: overwrite input)
  -h, --help          Show this help message

Log files for troubleshooting (appended on each run):
  $LOG_DIR/agent-annotate.log
      Main annotation agent — pipeline decisions, guard warnings

  $LOG_DIR/agent-splitter.log
      Call-graph analysis, topological ordering, per-function orchestration

  $LOG_DIR/agent-writer.log
      3-agent pipeline coordination (english → contract → invariant)

  $LOG_DIR/agent-english-writer.log
      English specification generation for each function

  $LOG_DIR/agent-contract-writer.log
      requires/ensures/assigns generation

  $LOG_DIR/agent-invariant-writer.log
      Loop invariant and variant generation

Tip: To watch progress in real-time:
  tail -f $LOG_DIR/agent-annotate.log

Examples:
  $(basename "$0") self/Module1_Ingestor.py
  $(basename "$0") src/pycsl/pycsl.py --out annotated_pycsl.py
  $(basename "$0") tests/to_annotate/001-basic-control-flow.py
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

# Default: annotate in-place
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

# Ensure log directory exists
mkdir -p "$LOG_DIR"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  PyCSL Annotation Pipeline                                  ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Input:  $INPUT_FILE"
echo "║  Output: $OUTPUT_FILE"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Run the annotation agent (stdout → log, stderr visible for errors)
AGENT_STDOUT_LOG="$LOG_DIR/agent-annotate-stdout.log"
set +e
python src/pycsl/agents/agent-annotate.py \
    --in "$INPUT_FILE" \
    --out "$OUTPUT_FILE" \
    > "$AGENT_STDOUT_LOG" 2>&1
RET_CODE=$?
set -e

echo ""
echo "────────────────────────────────────────────────────────────────"
if [[ $RET_CODE -eq 0 ]]; then
    echo "✓ Annotation complete: $OUTPUT_FILE"
else
    echo "✗ Annotation failed (exit code $RET_CODE)"
    echo ""
    echo "Last 10 lines of agent output:"
    tail -10 "$AGENT_STDOUT_LOG" 2>/dev/null || true
fi
echo ""
echo "Log files for troubleshooting:"
echo "  Agent stdout:     $AGENT_STDOUT_LOG"
echo "  Main agent:       $LOG_DIR/agent-annotate.log"
echo "  Call-graph:       $LOG_DIR/agent-splitter.log"
echo "  Writer pipeline:  $LOG_DIR/agent-writer.log"
echo "  English specs:    $LOG_DIR/agent-english-writer.log"
echo "  Contracts:        $LOG_DIR/agent-contract-writer.log"
echo "  Invariants:       $LOG_DIR/agent-invariant-writer.log"
echo "────────────────────────────────────────────────────────────────"

exit $RET_CODE
