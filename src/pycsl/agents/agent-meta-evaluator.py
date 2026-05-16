#!/usr/bin/env python3
"""
Agent Meta Evaluator — automated QA judge for the self-healing agentic pipeline.

Evaluates the efficacy and safety of each fix applied by agent-script-update by:
  1. Syntax-checking the modified file (py_compile for .py files)
  2. Re-running pycsl on the annotated file
  3. Classifying the outcome as Success / Partial Fix / Regression
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

AGENT_NAME = "agent-meta-evaluator"

try:
    from llm_client import log as _llm_log

    def log(msg: str, out_dir: Path) -> None:
        _llm_log(out_dir, AGENT_NAME, f"[{AGENT_NAME}] {msg}\n")
except ImportError:
    def log(msg: str, out_dir: Path) -> None:  # type: ignore[misc]
        print(f"[{AGENT_NAME}] {msg}")


def check_syntax(modified_file: Path, out_dir: Path) -> bool:
    """Return True if modified_file passes a syntax check."""
    if modified_file.suffix != ".py":
        return True  # Non-Python files (e.g. .md) pass by convention
    try:
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(modified_file)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            log(f"Syntax error in {modified_file.name}: {result.stderr.strip()}", out_dir)
        return result.returncode == 0
    except subprocess.SubprocessError as e:
        log(f"Syntax check subprocess error for {modified_file.name}: {e}", out_dir)
        return False


def run_pycsl(
    annotated_file: Path,
    pycsl_dir: Path,
    out_dir: Path,
) -> tuple[int, str, str]:
    """Re-run pycsl on annotated_file. Returns (returncode, stdout, stderr)."""
    pycsl_bin = pycsl_dir / "pycsl"
    cmd = [sys.executable, str(pycsl_bin), "--keep-mlw", str(annotated_file)]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
            cwd=pycsl_dir,
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.SubprocessError as e:
        log(f"pycsl subprocess error: {e}", out_dir)
        return 1, "", str(e)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="QA judge for the self-healing agentic pipeline"
    )
    parser.add_argument(
        "--annotated-file",
        dest="annotated_file",
        required=True,
        help="Path to the annotated .py file to re-verify with pycsl",
    )
    parser.add_argument(
        "--modified-file",
        dest="modified_file",
        required=True,
        help="Path to the file modified by agent-script-update (syntax-checked if .py)",
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Path to the output JSON evaluation file",
    )
    args = parser.parse_args()

    annotated_file = Path(args.annotated_file)
    modified_file = Path(args.modified_file)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_dir = out_path.parent

    log(f"annotated_file={annotated_file}, modified_file={modified_file}", out_dir)

    # Derive pycsl_dir: annotated_file lives in tests/annotated/, pycsl root is 2 levels up
    pycsl_dir = annotated_file.parent.parent.parent

    # 1. Syntax check
    syntax_valid = check_syntax(modified_file, out_dir)
    log(f"syntax_valid={syntax_valid}", out_dir)

    # 2. Pipeline re-verification
    if syntax_valid:
        ret_code, stdout, stderr = run_pycsl(annotated_file, pycsl_dir, out_dir)
    else:
        ret_code = 1
        stdout = ""
        stderr = "Syntax check failed — pycsl not re-run"

    log(f"pycsl returncode={ret_code}", out_dir)

    # 3. Status classification
    if syntax_valid and ret_code == 0:
        resolution_status = "Success"
    elif syntax_valid:
        resolution_status = "Partial Fix"
    else:
        resolution_status = "Regression"

    log(f"resolution_status={resolution_status}", out_dir)

    result = {
        "resolution_status": resolution_status,
        "new_ret_code": ret_code,
        "syntax_valid": syntax_valid,
        "stdout": stdout,
        "stderr": stderr,
    }
    try:
        from schema_validator import validate_or_warn
        validate_or_warn(result, "evaluator",
                         logger=lambda msg: log(msg, out_dir))
    except ImportError:
        pass
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"Wrote evaluation to {out_path}", out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
