#!/bin/bash
# PyCSL Coordinator Launch Script
# Runs the full annotation, proof, and reconciliation workflow,
# or re-runs individual meta-agents on already-existing metrics logs.
#
# Usage:
#   run.sh                        # full pipeline (default)
#   run.sh --start-at <N>         # start at file N (e.g. 10 → 010-*.py), annotated/ NOT cleaned
#   run.sh --review  <file-stem>  # re-run agent-meta-reviewer on existing metrics
#   run.sh --monitor <file-stem>  # re-run agent-meta-monitor  on existing logs
#   run.sh --evaluate <file-stem> <annotated-file> <modified-file>
#                                 # re-run agent-meta-evaluator on existing annotated file

set -e

PYCSL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_DIR="$PYCSL_DIR/src/pycsl/agents"
REPO_ROOT="$PYCSL_DIR"
METRICS_DIR="$PYCSL_DIR/metrics"
CONFIG_DIR="$PYCSL_DIR/config"

echo "================================================"
echo "PyCSL Coordinator Agent"
echo "================================================"
echo "PyCSL dir:  $PYCSL_DIR"
echo "Agents dir: $AGENTS_DIR"
echo "Repo root:  $REPO_ROOT"
echo ""

# Activate virtual environment if it exists
if [[ -f "$PYCSL_DIR/.venv/bin/activate" ]]; then
    echo "Activating Python virtual environment..."
    source "$PYCSL_DIR/.venv/bin/activate"
fi

# Ensure local Ollama is running (used for RAG embeddings)
EMBED_URL=$(python3 -c "import json; print(json.load(open('$CONFIG_DIR/agents-config.json')).get('nomic-embed-text-ollama-url','http://127.0.0.1:11434'))" 2>/dev/null || echo "http://127.0.0.1:11434")
if ! curl -sf "$EMBED_URL/api/tags" >/dev/null 2>&1; then
    echo "Starting local Ollama server..."
    ollama serve >/dev/null 2>&1 &
    OLLAMA_PID=$!
    for i in $(seq 1 15); do
        sleep 1
        curl -sf "$EMBED_URL/api/tags" >/dev/null 2>&1 && break
    done
    if ! curl -sf "$EMBED_URL/api/tags" >/dev/null 2>&1; then
        echo "WARNING: Could not start Ollama at $EMBED_URL"
    fi
fi
# Ensure embedding model is available
if curl -sf "$EMBED_URL/api/tags" 2>/dev/null | grep -q nomic-embed-text; then
    :
else
    echo "Pulling nomic-embed-text model..."
    OLLAMA_HOST="$EMBED_URL" ollama pull nomic-embed-text 2>/dev/null || true
fi

# Ensure Why3 detects available provers
why3 config detect >/dev/null 2>&1

cd "$PYCSL_DIR"

# ── helpers ────────────────────────────────────────────────────────────────────

check_provers() {
    local config_file="$CONFIG_DIR/agents-config.json"
    if [[ ! -f "$config_file" ]]; then
        echo "ERROR: Configuration file not found at $config_file"
        exit 1
    fi

    local missing_provers=()
    # Extract provers list, loop through, and split by comma to get the prover name
    while read -r prover_entry; do
        local prover_name="${prover_entry%%,*}"
        local prover_bin
        prover_bin="$(echo "$prover_name" | tr '[:upper:]' '[:lower:]')"
        if ! command -v "$prover_bin" >/dev/null 2>&1; then
            missing_provers+=("$prover_name")
        fi
    done < <(jq -r '.provers[]' "$config_file")

    if [[ ${#missing_provers[@]} -gt 0 ]]; then
        echo "ERROR: The following required provers were not found in PATH:"
        for p in "${missing_provers[@]}"; do
            echo "  - $p"
        done
        exit 1
    fi
    echo "✓ All required provers are available"
}

check_provers

usage() {
    echo "Usage:"
    echo "  run.sh                                             # full pipeline"
    echo "  run.sh --start-at <N>                             # start at file N (e.g. 10 → 010-*.py), keep annotated/"
    echo "  run.sh --review   <file-stem>                     # re-run meta-reviewer"
    echo "  run.sh --monitor  <file-stem>                     # re-run meta-monitor"
    echo "  run.sh --evaluate <file-stem> <annotated-file> <modified-file>"
    echo "                                                     # re-run meta-evaluator"
    exit 1
}

run_reviewer() {
    local stem="$1"
    local reconcile_json="$METRICS_DIR/reviewer/${stem}.json"
    local eval_json
    eval_json=$(ls "$METRICS_DIR/evaluator/${stem}_"*.json 2>/dev/null | sort -V | tail -1 || true)
    local monitor_json="$METRICS_DIR/monitor/${stem}.json"
    local out_json="$METRICS_DIR/reviewer/${stem}.json"
    local out_md="$METRICS_DIR/reviewer/${stem}.md"

    # Prefer the reconcile JSON from the main pycsl dir if it exists
    local pycsl_reconcile
    pycsl_reconcile=$(ls "$PYCSL_DIR/reconcile_${stem}"*.json 2>/dev/null | sort -V | tail -1 || true)
    [[ -n "$pycsl_reconcile" ]] && reconcile_json="$pycsl_reconcile"

    echo "Re-running agent-meta-reviewer for stem: $stem"
    echo "  reconcile-json : $reconcile_json"
    echo "  eval-json      : ${eval_json:-(none)}"
    echo "  monitor-json   : $monitor_json"
    echo "  out-json       : $out_json"
    echo "  out-md         : $out_md"
    echo ""

    python "$AGENTS_DIR/agent-meta-reviewer.py" \
        --reconcile-json "$reconcile_json" \
        --eval-json      "${eval_json:-/dev/null}" \
        --monitor-json   "$monitor_json" \
        --out-json       "$out_json" \
        --out-md         "$out_md" \
        --config         "$CONFIG_DIR/agents-config.json"
}

run_monitor() {
    local stem="$1"
    local combined_reconcile="$METRICS_DIR/logs/reconcile_${stem}_combined.log"
    local combined_update="$METRICS_DIR/logs/update_${stem}_combined.log"
    local out_json="$METRICS_DIR/monitor/${stem}.json"

    echo "Re-running agent-meta-monitor for stem: $stem"
    echo "  reconcile-log : $combined_reconcile"
    echo "  update-log    : $combined_update"
    echo "  out           : $out_json"
    echo ""

    python "$AGENTS_DIR/agent-meta-monitor.py" \
        --reconcile-log "$combined_reconcile" \
        --update-log    "$combined_update" \
        --out           "$out_json"
}

run_evaluator() {
    local stem="$1"
    local annotated_file="$2"
    local modified_file="$3"
    # Use a new sequential attempt number beyond existing evaluator outputs
    local attempt
    attempt=$(ls "$METRICS_DIR/evaluator/${stem}_"*.json 2>/dev/null | wc -l || echo 0)
    local out_json="$METRICS_DIR/evaluator/${stem}_${attempt}.json"

    echo "Re-running agent-meta-evaluator for stem: $stem"
    echo "  annotated-file : $annotated_file"
    echo "  modified-file  : $modified_file"
    echo "  out            : $out_json"
    echo ""

    python "$AGENTS_DIR/agent-meta-evaluator.py" \
        --annotated-file "$annotated_file" \
        --modified-file  "$modified_file" \
        --out            "$out_json"
}

# ── dispatch ───────────────────────────────────────────────────────────────────

case "${1:-}" in
    --start-at)
        [[ -z "${2:-}" ]] && { echo "ERROR: --start-at requires a number"; usage; }
        echo "Starting coordinator agent (--start-at $2)..."
        python "$AGENTS_DIR/coordinator.py" --pycsl-dir "$PYCSL_DIR" --start-at "$2"
        EXIT_CODE=$?
        ;;
    --review)
        [[ -z "${2:-}" ]] && { echo "ERROR: --review requires a file stem"; usage; }
        run_reviewer "$2"
        EXIT_CODE=$?
        ;;
    --monitor)
        [[ -z "${2:-}" ]] && { echo "ERROR: --monitor requires a file stem"; usage; }
        run_monitor "$2"
        EXIT_CODE=$?
        ;;
    --evaluate)
        [[ -z "${2:-}" || -z "${3:-}" || -z "${4:-}" ]] && {
            echo "ERROR: --evaluate requires <file-stem> <annotated-file> <modified-file>"
            usage
        }
        run_evaluator "$2" "$3" "$4"
        EXIT_CODE=$?
        ;;
    --help|-h)
        usage
        ;;
    "")
        echo "Starting coordinator agent (full pipeline)..."
        python "$AGENTS_DIR/coordinator.py" --pycsl-dir "$PYCSL_DIR"
        EXIT_CODE=$?
        ;;
    *)
        echo "ERROR: Unknown option: $1"
        usage
        ;;
esac

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✓ Completed successfully"
elif [[ $EXIT_CODE -eq 72 ]]; then
    echo "✗ Halted — max retries (10) exhausted (exit 72)"
    echo "  Check metrics/reviewer/ for the automated report"
elif [[ $EXIT_CODE -eq 73 ]]; then
    echo "✗ Halted — loop detected, human review required (exit 73)"
    echo "  Check metrics/reviewer/ for the automated report"
else
    echo "✗ Failed with exit code $EXIT_CODE"
fi

exit $EXIT_CODE

