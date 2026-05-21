#!/usr/bin/env bash
# Invoke agent-splitter.py on a Python file with optional --class/--fun filtering.
#
# Usage:
#   ./bin/call-agent-splitter.sh <input.py>
#   ./bin/call-agent-splitter.sh <input.py> --out <output.py>
#   ./bin/call-agent-splitter.sh <input.py> --class MyClass --fun my_method
#   ./bin/call-agent-splitter.sh --help
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

LOG_DIR="$PROJECT_ROOT/my_project/log"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <input.py>

Run the PyCSL agent-splitter pipeline on a Python file.  The splitter parses
the file, builds a call graph, topologically sorts functions, and invokes the
3-agent writer pipeline (english → contracts → invariants) on each function.

Arguments:
  <input.py>          Python source file to annotate

Options:
  --out <file>        Write annotated output to <file> (default: <input>_annotated.py)
  --class <name>      Only annotate methods of this class
  --fun <name>        Only annotate function(s) with this name
  --resume            Resume from checkpoint (skip already-annotated functions)
  --verbose           Show detailed per-step diagnostic output
  -h, --help          Show this help message

When both --class and --fun are given, only ClassName.function_name is
annotated.  The call-graph analysis still runs on the full file so that
callee contracts are available as context.

Log files (appended on each run):
  $LOG_DIR/agent-splitter.log
  $LOG_DIR/agent-writer.log
  $LOG_DIR/agent-english-writer.log
  $LOG_DIR/agent-contract-writer.log
  $LOG_DIR/agent-invariant-writer.log

Examples:
  $(basename "$0") src/pycsl/Module6_WhyMLTranspiler.py
  $(basename "$0") src/pycsl/Module6_WhyMLTranspiler.py --class IRScanner --fun uses_arrayset
  $(basename "$0") src/pycsl/pycsl.py --fun main --out pycsl_annotated.py
EOF
}

# Parse arguments
INPUT_FILE=""
OUTPUT_FILE=""
FILTER_CLASS=""
FILTER_FUN=""
RESUME=""
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --out)
            [[ $# -lt 2 ]] && { echo "Error: --out requires a file argument" >&2; exit 1; }
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --class)
            [[ $# -lt 2 ]] && { echo "Error: --class requires a name argument" >&2; exit 1; }
            FILTER_CLASS="$2"
            shift 2
            ;;
        --fun)
            [[ $# -lt 2 ]] && { echo "Error: --fun requires a name argument" >&2; exit 1; }
            FILTER_FUN="$2"
            shift 2
            ;;
        --resume)
            RESUME="1"
            shift
            ;;
        --verbose)
            VERBOSE="1"
            shift
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

# Default output: <basename>_annotated.py next to the input
if [[ -z "$OUTPUT_FILE" ]]; then
    dir="$(dirname "$INPUT_FILE")"
    base="$(basename "$INPUT_FILE" .py)"
    OUTPUT_FILE="${dir}/${base}_annotated.py"
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

# Build splitter command
SPLITTER_CMD=(
    python src/pycsl/agents/agent-splitter.py
    --in "$INPUT_FILE"
    --out "$OUTPUT_FILE"
)
[[ -n "$FILTER_CLASS" ]] && SPLITTER_CMD+=(--class "$FILTER_CLASS")
[[ -n "$FILTER_FUN" ]]   && SPLITTER_CMD+=(--fun "$FILTER_FUN")
[[ -n "$RESUME" ]]       && SPLITTER_CMD+=(--resume)
[[ -n "$VERBOSE" ]]      && SPLITTER_CMD+=(--verbose)

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  PyCSL Agent-Splitter Pipeline                               ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║  Input:  $INPUT_FILE"
[[ -n "$FILTER_CLASS" ]] && echo "║  Class:  $FILTER_CLASS"
[[ -n "$FILTER_FUN" ]]   && echo "║  Fun:    $FILTER_FUN"
[[ -n "$RESUME" ]]       && echo "║  Resume: yes"
[[ -n "$VERBOSE" ]]      && echo "║  Verbose: yes"
echo "║  Output: $OUTPUT_FILE"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

SPLITTER_LOG="$LOG_DIR/agent-splitter-stdout.log"
SPLITTER_ERR="$LOG_DIR/agent-splitter-stderr.log"
set +e
# stdout → log only; stderr → terminal AND log (via tee)
"${SPLITTER_CMD[@]}" > "$SPLITTER_LOG" 2> >(tee -a "$SPLITTER_ERR" >&2)
RET_CODE=$?
set -e

echo ""
echo "────────────────────────────────────────────────────────────────"
if [[ $RET_CODE -eq 0 ]]; then
    echo "✓ Annotation complete: $OUTPUT_FILE"
else
    echo "✗ Annotation failed (exit code $RET_CODE)"
    echo ""
    echo "Last 10 lines of output:"
    tail -10 "$SPLITTER_LOG" 2>/dev/null || true
fi
echo ""
echo "Log files:"
echo "  Stdout:       $SPLITTER_LOG"
echo "  Stderr:       $SPLITTER_ERR"
echo "  Splitter:     $LOG_DIR/agent-splitter.log"
echo "  Writer:       $LOG_DIR/agent-writer.log"
echo "  English:      $LOG_DIR/agent-english-writer.log"
echo "  Contracts:    $LOG_DIR/agent-contract-writer.log"
echo "  Invariants:   $LOG_DIR/agent-invariant-writer.log"
echo "────────────────────────────────────────────────────────────────"

exit $RET_CODE
