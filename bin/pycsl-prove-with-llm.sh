#!/usr/bin/env bash
# Prove a PyCSL-annotated Python file, using Rocq + the LLM proof writer only
# when SMT provers cannot discharge all goals.
#
# Usage:
#   ./bin/pycsl-prove-with-llm.sh <input.py>
#   ./bin/pycsl-prove-with-llm.sh --proof-dir <dir> <input.py>
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <input.py>

Prove an already annotated PyCSL file. If normal pycsl verification succeeds,
the script exits without creating Rocq artifacts. If SMT leaves goals unproven,
the script creates a proof directory, generates Rocq .v skeletons, runs the
LLM Rocq proof writer on them, and finally replays the resulting proofs.

Arguments:
  <input.py>            PyCSL-annotated Python file to verify

Options:
  --proof-dir <dir>     Use <dir> instead of the default <input>.proofs/
  -h, --help            Show this help message

Examples:
  $(basename "$0") test-suite/corpus/pycsl-reference/0288.py
  $(basename "$0") --proof-dir /tmp/proofs myfile.py
EOF
}

resolve_abs() {
    python3 - "$1" <<'PY'
import os
import sys
print(os.path.abspath(sys.argv[1]))
PY
}

INPUT_FILE=""
PROOF_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        --proof-dir)
            if [[ $# -lt 2 ]]; then
                echo "Error: --proof-dir requires a directory argument" >&2
                exit 1
            fi
            PROOF_DIR="$2"
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

INPUT_ABS="$(resolve_abs "$INPUT_FILE")"
if [[ -z "$PROOF_DIR" ]]; then
    PROOF_DIR="${INPUT_ABS%.py}.proofs"
else
    PROOF_DIR="$(resolve_abs "$PROOF_DIR")"
fi

if [[ -f "$PROJECT_ROOT/.venv/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

PYTHON="${PYTHON:-}"
if [[ -z "$PYTHON" ]]; then
    if [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
        PYTHON="$PROJECT_ROOT/.venv/bin/python"
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON="$(command -v python3)"
    else
        echo "Error: python3 not found" >&2
        exit 1
    fi
fi

PYCSL="$PROJECT_ROOT/src/pycsl/pycsl.py"
ROCQ_AGENT="$PROJECT_ROOT/src/pycsl/agents/agent-rocq-proof-writer.py"

if [[ ! -f "$PYCSL" ]]; then
    echo "Error: pycsl entrypoint not found at $PYCSL" >&2
    exit 1
fi

if [[ ! -f "$ROCQ_AGENT" ]]; then
    echo "Error: Rocq proof writer not found at $ROCQ_AGENT" >&2
    exit 1
fi

prepare_proof_dir() {
    local dir="$1"
    mkdir -p "$dir"
    rm -f \
        "$dir"/*.v \
        "$dir"/*.mlw \
        "$dir"/*.glob \
        "$dir"/*.vo \
        "$dir"/*.vok \
        "$dir"/*.vos \
        "$dir"/*.llm.log \
        "$dir"/Makefile
}

find_or_normalize_mlw() {
    local dir="$1"
    local input_abs="$2"
    local desired="$dir/$(basename "${input_abs%.py}").mlw"
    local temp="$dir/.pycsl_temp.mlw"

    if [[ -f "$temp" ]]; then
        mv -f "$temp" "$desired"
    fi

    if [[ -f "$desired" ]]; then
        printf '%s\n' "$desired"
        return 0
    fi

    shopt -s nullglob
    local mlws=("$dir"/*.mlw)
    shopt -u nullglob
    if [[ ${#mlws[@]} -gt 0 ]]; then
        printf '%s\n' "${mlws[0]}"
        return 0
    fi

    printf '\n'
}

cleanup_source_mlw() {
    local input_abs="$1"
    local source_mlw="${input_abs%.py}.mlw"
    if [[ -f "$source_mlw" ]]; then
        rm -f "$source_mlw"
    fi
}

write_makefile() {
    local dir="$1"
    local input_abs="$2"
    local makefile="$dir/Makefile"
    cat > "$makefile" <<EOF
SHELL := /bin/bash

PROJECT_ROOT := $PROJECT_ROOT
PYTHON := $PYTHON
PYCSL := \$(PROJECT_ROOT)/src/pycsl/pycsl.py
ROCQ_AGENT := \$(PROJECT_ROOT)/src/pycsl/agents/agent-rocq-proof-writer.py
INPUT := $input_abs
PROOF_DIR := \$(CURDIR)

.PHONY: help replay coq llm clean

help:
	@echo "Targets:"
	@echo "  make replay  - replay proofs with pycsl --rocq-proofs"
	@echo "  make coq     - compile all .v files with coqc"
	@echo "  make llm     - rerun agent-rocq-proof-writer.py on all .v files"
	@echo "  make clean   - remove Rocq compilation artifacts and *.llm.log"

replay:
	cd "\$(PROJECT_ROOT)" && "\$(PYTHON)" "\$(PYCSL)" --rocq-proofs "\$(PROOF_DIR)" "\$(INPUT)"

coq:
	"\$(PROJECT_ROOT)/bin/run-rocq-proofs.sh" "\$(PROOF_DIR)"

llm:
	@set -euo pipefail; \
	shopt -s nullglob; \
	mlw=""; \
	for f in "\$(CURDIR)"/*.mlw; do mlw="\$\$f"; break; done; \
	count=0; \
	for v in "\$(CURDIR)"/*.v; do \
		count=\$\$((count + 1)); \
		echo "[*] LLM proof \$\$v"; \
		if [[ -n "\$\$mlw" ]]; then \
			cd "\$(PROJECT_ROOT)" && "\$(PYTHON)" "\$(ROCQ_AGENT)" --in "\$\$v" --out "\$\$v" --mlw "\$\$mlw"; \
		else \
			cd "\$(PROJECT_ROOT)" && "\$(PYTHON)" "\$(ROCQ_AGENT)" --in "\$\$v" --out "\$\$v"; \
		fi; \
	done; \
	if [[ \$\$count -eq 0 ]]; then \
		echo "[!] No .v files found in \$(CURDIR)"; \
		exit 1; \
	fi

clean:
	rm -f *.glob *.vo *.vok *.vos *.llm.log *~
EOF
}

run_llm_loop() {
    local dir="$1"
    local mlw="$2"
    local total=0
    local ok=0
    local failed=0

    shopt -s nullglob
    local vfiles=("$dir"/*.v)
    shopt -u nullglob

    if [[ ${#vfiles[@]} -eq 0 ]]; then
        echo "[!] No Rocq .v proof obligations were generated in $dir" >&2
        return 1
    fi

    for vfile in "${vfiles[@]}"; do
        total=$((total + 1))
        local log_file="$dir/$(basename "${vfile%.v}").llm.log"
        echo "[*] LLM Rocq proof attempt: $(basename "$vfile")"
        if [[ -n "$mlw" && -f "$mlw" ]]; then
            if (cd "$PROJECT_ROOT" && "$PYTHON" "$ROCQ_AGENT" --in "$vfile" --out "$vfile" --mlw "$mlw") >"$log_file" 2>&1; then
                echo "    [ok] completed"
                ok=$((ok + 1))
            else
                echo "    [fail] incomplete - see $log_file"
                failed=$((failed + 1))
            fi
        else
            if (cd "$PROJECT_ROOT" && "$PYTHON" "$ROCQ_AGENT" --in "$vfile" --out "$vfile") >"$log_file" 2>&1; then
                echo "    [ok] completed"
                ok=$((ok + 1))
            else
                echo "    [fail] incomplete - see $log_file"
                failed=$((failed + 1))
            fi
        fi
    done

    echo "[*] LLM proof summary: $ok succeeded, $failed failed, $total total"
    return 0
}

echo "[*] PyCSL prove-with-llm"
echo "[*] Input: $INPUT_ABS"
echo "[*] Proof dir: $PROOF_DIR"
echo ""

echo "[*] Step 1: Running normal pycsl verification..."
set +e
(cd "$PROJECT_ROOT" && "$PYTHON" "$PYCSL" "$INPUT_ABS")
FAST_RC=$?
set -e

if [[ $FAST_RC -eq 0 ]]; then
    echo ""
    echo "[+] Verification succeeded automatically - no Rocq/LLM fallback needed."
    exit 0
fi

echo ""
echo "[*] Automatic proof did not succeed (exit $FAST_RC)."
echo "[*] Step 2: Generating Rocq proof skeletons in $PROOF_DIR ..."
prepare_proof_dir "$PROOF_DIR"

set +e
(cd "$PROJECT_ROOT" && "$PYTHON" "$PYCSL" --keep-mlw --rocq "$PROOF_DIR" "$INPUT_ABS")
ROCQ_RC=$?
set -e

if [[ $ROCQ_RC -ne 0 && $ROCQ_RC -ne 2 ]]; then
    cleanup_source_mlw "$INPUT_ABS"
    echo "[!] pycsl --rocq failed unexpectedly (exit $ROCQ_RC)." >&2
    exit "$ROCQ_RC"
fi

MLW_PATH="$(find_or_normalize_mlw "$PROOF_DIR" "$INPUT_ABS")"
cleanup_source_mlw "$INPUT_ABS"
write_makefile "$PROOF_DIR" "$INPUT_ABS"

shopt -s nullglob
VFILES=("$PROOF_DIR"/*.v)
shopt -u nullglob
if [[ ${#VFILES[@]} -eq 0 ]]; then
    echo "[!] No Rocq .v files were generated in $PROOF_DIR" >&2
    echo "    Manual follow-up:"
    echo "      why3 ide ${MLW_PATH:-<missing .mlw>}"
    exit 1
fi

echo ""
echo "[*] Step 3: Running agent-rocq-proof-writer.py on generated obligations..."
run_llm_loop "$PROOF_DIR" "$MLW_PATH" || true

echo ""
echo "[*] Step 4: Replaying proofs with pycsl --rocq-proofs ..."
set +e
(cd "$PROJECT_ROOT" && "$PYTHON" "$PYCSL" --rocq-proofs "$PROOF_DIR" "$INPUT_ABS")
FINAL_RC=$?
set -e

echo ""
if [[ $FINAL_RC -eq 0 ]]; then
    echo "[+] Verification succeeded after Rocq/LLM fallback."
else
    echo "[-] Verification still incomplete after automatic Rocq/LLM fallback."
    echo "    Proof artifacts kept in: $PROOF_DIR"
    echo "    Useful follow-up commands:"
    echo "      cd \"$PROOF_DIR\" && make llm"
    echo "      cd \"$PROOF_DIR\" && make coq"
    echo "      cd \"$PROOF_DIR\" && make replay"
fi

exit "$FINAL_RC"
