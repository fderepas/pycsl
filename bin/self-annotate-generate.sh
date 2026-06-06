#!/usr/bin/env bash
# Generate annotated copies of src/pycsl/*.py into src/self-annotate/{rocq,lean}/
# using the agent annotation pipeline, then verify each file with pycsl --no-proof.
#
# Usage:
#   ./bin/self-annotate-generate.sh                    # both paths, all files
#   ./bin/self-annotate-generate.sh --path rocq        # one path only
#   ./bin/self-annotate-generate.sh --file Module5_IREmitter.py  # one file, both paths
#   ./bin/self-annotate-generate.sh --path lean --file ir_schema.py
#   ./bin/self-annotate-generate.sh --help
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/my_project/log"

# --------------------------------------------------------------------------
# File processing order (global plan §9.2 — dependency-safe).
# Each entry is: "<file> <phase> <annotation-mode>"
#   annotation-mode = copy  → no contracts, just cp
#   annotation-mode = annotate → agent-annotate + infer-invariants + verify
# --------------------------------------------------------------------------
declare -a FILE_ORDER=(
    "__init__.py:0:copy"
    "errors.py:0:copy"
    "ir_schema.py:1:annotate"
    "Module3_Weaver.py:2:annotate"
    "ConcurrencyChecker.py:2:annotate"
    "Module2_Parser.py:3:annotate"
    "Module1_Ingestor.py:4:annotate"
    "Module4_SemanticAnalyzer.py:4:annotate"
    "Module5_IREmitter.py:5:annotate"
    "pycsl.py:6:annotate"
    "Module6_WhyMLTranspiler.py:7:annotate"
)

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS]

Generate annotated copies of src/pycsl/*.py into src/self-annotate/{rocq,lean}/
using the agent annotation pipeline.

For each non-trivial file the pipeline runs:
  1. agent-annotate.py      — add requires/ensures/assigns
  2. agent-infer-invariants — add loop invariant/variant
  3. pycsl --no-proof       — verify WhyML generation

Files outside the formal model (errors.py, __init__.py) are copied verbatim.

Options:
  --path rocq|lean     Process only this path (default: both)
  --file <name>        Process only this file (default: all files)
  -h, --help           Show this help message

Log files:
  $LOG_DIR/self-annotate-generate.log
  $LOG_DIR/agent-annotate.log
  $LOG_DIR/agent-infer-invariants.log
EOF
}

# --------------------------------------------------------------------------
# Argument parsing
# --------------------------------------------------------------------------
PATHS=("rocq" "lean")
SINGLE_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage; exit 0 ;;
        --path)
            [[ $# -lt 2 ]] && { echo "Error: --path requires rocq or lean" >&2; exit 1; }
            case "$2" in
                rocq|lean) PATHS=("$2") ;;
                *) echo "Error: --path must be 'rocq' or 'lean'" >&2; exit 1 ;;
            esac
            shift 2 ;;
        --file)
            [[ $# -lt 2 ]] && { echo "Error: --file requires a filename" >&2; exit 1; }
            SINGLE_FILE="$2"
            shift 2 ;;
        *)
            echo "Error: unknown option '$1'" >&2
            echo "Run '$(basename "$0") --help' for usage." >&2
            exit 1 ;;
    esac
done

# --------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------
cd "$PROJECT_ROOT"
if [[ -f .venv/bin/activate ]]; then
    source .venv/bin/activate
else
    echo "Error: virtual environment not found at $PROJECT_ROOT/.venv" >&2
    exit 1
fi
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/self-annotate-generate.log"
: > "$LOG_FILE"

_log() { echo "$*" | tee -a "$LOG_FILE"; }
_logf() { printf "$@" | tee -a "$LOG_FILE"; }

# --------------------------------------------------------------------------
# Per-file annotation function
# --------------------------------------------------------------------------
_process_file() {
    local path="$1"      # rocq or lean
    local filename="$2"  # e.g. Module5_IREmitter.py
    local mode="$3"      # copy or annotate

    local src="src/pycsl/$filename"
    local dst="src/self-annotate/$path/$filename"

    if [[ ! -f "$src" ]]; then
        _log "  SKIP  $filename — source not found at $src"
        return 0
    fi

    if [[ "$mode" == "copy" ]]; then
        cp "$src" "$dst"
        _log "  COPY  [$path] $filename"
        return 0
    fi

    # Keep a backup of the existing file (if any) so we can restore on failure
    local backup=""
    if [[ -f "$dst" ]]; then
        backup=$(mktemp)
        cp "$dst" "$backup"
    fi

    # Returns 0 if backup restored (warn only), 1 if no backup (hard fail)
    _restore_or_warn() {
        local msg="$1"
        if [[ -n "$backup" && -f "$backup" ]]; then
            cp "$backup" "$dst"
            rm -f "$backup"
            _log "  WARN  [$path] $filename — $msg"
            _log "        restored previous annotated file; running pycsl --no-proof on it"
            local vfy
            vfy=$(python src/pycsl/pycsl.py --no-proof "$dst" 2>&1)
            if echo "$vfy" | grep -q 'SUCCESS'; then
                _log "  PASS  [$path] $filename (from previous)"
                return 0
            else
                _log "  FAIL  [$path] $filename — restored file also fails pycsl:"
                echo "$vfy" | head -10 | while IFS= read -r line; do _log "        $line"; done
                return 1
            fi
        else
            _log "  FAIL  [$path] $filename — $msg (no previous file to restore)"
            return 1
        fi
    }

    # --- Step 1: agent-annotate ---
    _log "  ANN   [$path] $filename — running agent-annotate ..."
    if ! python src/pycsl/agents/agent-annotate.py \
            --in "$src" \
            --out "$dst" \
            >> "$LOG_DIR/agent-annotate-stdout.log" 2>&1; then
        _restore_or_warn "agent-annotate failed (see $LOG_DIR/agent-annotate-stdout.log)" || return 1
    fi

    # --- Step 2: Python syntax check (before invariant inference) ---
    _log "  SYN   [$path] $filename — checking Python syntax ..."
    local syn_err
    if ! syn_err=$(python -c "import ast; ast.parse(open('$dst').read())" 2>&1); then
        local short_err
        short_err=$(echo "$syn_err" | grep -E 'SyntaxError|line [0-9]' | head -3 || true)
        _restore_or_warn "broken Python syntax after annotation: ${short_err}" || return 1
    fi

    # --- Step 3: agent-infer-invariants ---
    _log "  INV   [$path] $filename — inferring loop invariants ..."
    if ! python src/pycsl/agents/agent-infer-invariants.py \
            --in "$dst" \
            --out "$dst" \
            >> "$LOG_DIR/agent-infer-invariants-stdout.log" 2>&1; then
        _log "  WARN  [$path] $filename — invariant inference failed; continuing with agent-annotate output"
    fi

    # --- Step 4: pycsl --no-proof ---
    _log "  VFY   [$path] $filename — pycsl --no-proof ..."
    local pycsl_out
    pycsl_out=$(python src/pycsl/pycsl.py --no-proof "$dst" 2>&1)
    if echo "$pycsl_out" | grep -q 'SUCCESS'; then
        _log "  PASS  [$path] $filename"
        rm -f "$backup"
    else
        echo "$pycsl_out" | head -20 | while IFS= read -r line; do _log "        $line"; done
        _restore_or_warn "pycsl --no-proof failed" || return 1
    fi
}

# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
FAIL_COUNT=0
START_TIME=$(date +%s)

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  PyCSL Self-Annotation Generator                            ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Paths: %-52s ║\n" "${PATHS[*]}"
if [[ -n "$SINGLE_FILE" ]]; then
    printf "║  File:  %-52s ║\n" "$SINGLE_FILE"
else
    echo "║  Files: all (phase order 0–7)                               ║"
fi
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
_log "Started: $(date)"
_log ""

for path in "${PATHS[@]}"; do
    _log "=== Path: $path ==="
    mkdir -p "src/self-annotate/$path"

    for entry in "${FILE_ORDER[@]}"; do
        IFS=':' read -r filename phase mode <<< "$entry"

        # If --file was given, skip all other files
        if [[ -n "$SINGLE_FILE" && "$filename" != "$SINGLE_FILE" ]]; then
            continue
        fi

        if ! _process_file "$path" "$filename" "$mode"; then
            (( FAIL_COUNT++ )) || true
        fi
    done
    _log ""
done

END_TIME=$(date +%s)
ELAPSED=$(( END_TIME - START_TIME ))

echo ""
echo "────────────────────────────────────────────────────────────────"
if [[ $FAIL_COUNT -eq 0 ]]; then
    echo "✓ All files generated successfully (${ELAPSED}s)"
    _log "Result: SUCCESS (${ELAPSED}s, 0 failures)"
else
    echo "✗ $FAIL_COUNT file(s) failed — see $LOG_FILE"
    _log "Result: FAILED (${ELAPSED}s, $FAIL_COUNT failures)"
fi
echo "Log: $LOG_FILE"
echo "────────────────────────────────────────────────────────────────"

[[ $FAIL_COUNT -eq 0 ]]
