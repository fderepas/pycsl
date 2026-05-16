#!/usr/bin/env bash
# get-meta-info.sh — Query meta-agent outputs for a given file stem.
#
# Usage:
#   bin/get-meta-info.sh <stem>           # show all meta-agent results for <stem>
#   bin/get-meta-info.sh --all            # list all available stems
#   bin/get-meta-info.sh <stem> --json    # raw JSON output (no formatting)
#
# Examples:
#   bin/get-meta-info.sh 001-basic-control-flow
#   bin/get-meta-info.sh --all

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
METRICS_DIR="$REPO_DIR/metrics"

json_mode=false

usage() {
    echo "Usage: get-meta-info.sh <stem> [--json] | --all"
    echo ""
    echo "  <stem>     File stem (e.g. 001-basic-control-flow)"
    echo "  --all      List all available stems with meta-agent data"
    echo "  --json     Output raw JSON instead of formatted text"
    exit 1
}

# ── --all: list stems ──────────────────────────────────────────────────────────

list_all() {
    echo "Available stems with meta-agent data:"
    echo ""
    local stems=()
    for dir in evaluator monitor reviewer; do
        if [[ -d "$METRICS_DIR/$dir" ]]; then
            for f in "$METRICS_DIR/$dir"/*.json; do
                [[ -f "$f" ]] || continue
                local base
                base="$(basename "$f" .json)"
                base="${base%_[0-9]*}"
                stems+=("$base")
            done
        fi
    done
    if [[ ${#stems[@]} -eq 0 ]]; then
        echo "  (none — run bin/run.sh first)"
    else
        printf '%s\n' "${stems[@]}" | sort -u | sed 's/^/  /'
    fi
}

# ── show one stem ──────────────────────────────────────────────────────────────

show_section() {
    local title="$1"
    local file="$2"

    if [[ ! -f "$file" ]]; then
        echo "  $title: (not found)"
        return
    fi

    if $json_mode; then
        echo "--- $title ---"
        cat "$file"
    else
        echo "  $title:"
        if command -v jq >/dev/null 2>&1; then
            jq '.' "$file" | sed 's/^/    /'
        else
            python3 -m json.tool "$file" 2>/dev/null | sed 's/^/    /' || cat "$file" | sed 's/^/    /'
        fi
    fi
    echo ""
}

show_stem() {
    local stem="$1"

    echo "╔══════════════════════════════════════════════╗"
    echo "  Meta-agent results for: $stem"
    echo "╚══════════════════════════════════════════════╝"
    echo ""

    # Evaluator (may have multiple attempts)
    local eval_files
    eval_files=$(ls "$METRICS_DIR/evaluator/${stem}_"*.json 2>/dev/null | sort -V || true)
    if [[ -n "$eval_files" ]]; then
        for ef in $eval_files; do
            local attempt
            attempt="$(basename "$ef" .json | sed "s/${stem}_//")"
            show_section "Evaluator (attempt $attempt)" "$ef"
        done
    else
        echo "  Evaluator: (no data)"
        echo ""
    fi

    # Monitor
    show_section "Monitor" "$METRICS_DIR/monitor/${stem}.json"

    # Reviewer JSON
    show_section "Reviewer" "$METRICS_DIR/reviewer/${stem}.json"

    # Reviewer Markdown (show if exists)
    local md_file="$METRICS_DIR/reviewer/${stem}.md"
    if [[ -f "$md_file" ]]; then
        echo "  Reviewer report (Markdown):"
        sed 's/^/    /' "$md_file"
        echo ""
    fi
}

# ── parse args ─────────────────────────────────────────────────────────────────

if [[ $# -eq 0 ]]; then
    usage
fi

stem=""
for arg in "$@"; do
    case "$arg" in
        --all)  list_all; exit 0 ;;
        --json) json_mode=true ;;
        -h|--help) usage ;;
        -*) echo "Unknown option: $arg"; usage ;;
        *)  stem="$arg" ;;
    esac
done

if [[ -z "$stem" ]]; then
    echo "ERROR: stem argument required"
    usage
fi

if [[ ! -d "$METRICS_DIR" ]]; then
    echo "ERROR: metrics/ directory not found. Run bin/run.sh first."
    exit 1
fi

show_stem "$stem"
