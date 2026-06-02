"""Statement extractors for Rocq and Lean (proof2why3 v0).

Invokes `coqc` / `lake env lean` on a companion script that runs
`Check <qualname>.` (Rocq) or `#check @<qualname>` (Lean) and parses
the type signature out of stdout.

The output is a raw string per qualname (the prover's pretty-printed
type). Normalization to a canonical form happens in `normalize.py`.

v0 limitation: this extraction is line-oriented on the prover's
pretty-printer output. Stable enough for the gcd-family demo; a
robust production extractor should use sertop (Rocq) and Lean
metaprogramming (Phase 1+2 in sticky-01.md).
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List


def extract_rocq_statements(proof_file: Path,
                             qualnames: List[str]) -> Dict[str, str]:
    """Return {qualname: rendered_type_string} for each cited qualname.

    Compiles the proof file in-place (-R . "" so unqualified `Require
    Import <file>` resolves), then runs a companion .v file that
    issues `Check <qualname>.` for each name. Parses stdout into the
    per-qualname blocks.
    """
    proof_dir = proof_file.parent
    module_name = proof_file.stem  # e.g., "gcd"

    # Compile the proof file first (idempotent if already done).
    subprocess.run(
        ["coqc", "-R", str(proof_dir), "", proof_file.name],
        cwd=str(proof_dir), capture_output=True, text=True, timeout=180,
    )

    lines = [f"Require Import {module_name}.",
             "Set Printing Width 1000."]
    for qn in qualnames:
        lines.append(f"Check {qn}.")
    companion = "\n".join(lines) + "\n"
    with tempfile.NamedTemporaryFile(
        suffix=".v", dir=str(proof_dir), delete=False, mode="w",
    ) as tf:
        tf.write(companion)
        companion_path = Path(tf.name)
    try:
        res = subprocess.run(
            ["coqc", "-R", str(proof_dir), "", companion_path.name],
            cwd=str(proof_dir), capture_output=True, text=True, timeout=120,
        )
        stdout = res.stdout
    finally:
        try:
            companion_path.unlink()
        except OSError:
            pass
        for ext in (".vo", ".vok", ".vos", ".glob"):
            stale = proof_dir / (companion_path.stem + ext)
            try:
                stale.unlink()
            except FileNotFoundError:
                pass

    return _split_rocq_check_output(stdout, qualnames)


def _split_rocq_check_output(stdout: str,
                              qualnames: List[str]) -> Dict[str, str]:
    """Slice coqc stdout into per-qualname Check blocks.

    Each block looks like:
        <qualname>
             : <type-pretty-printed>

    Successive blocks are separated by a blank line.
    """
    result: Dict[str, str] = {}
    # Lookahead per qualname (qualnames printed in source order).
    # Each block starts with the qualname on its own line, followed by
    # an indented `: <type>` continuation.
    lines = stdout.splitlines()
    i = 0
    for qn in qualnames:
        # Find the start of this block.
        while i < len(lines):
            if lines[i].strip() == qn:
                i += 1
                break
            i += 1
        # Collect the type lines: starts with whitespace + ":" then
        # may continue across multiple indented lines.
        block: List[str] = []
        if i < len(lines) and lines[i].lstrip().startswith(": "):
            block.append(lines[i].lstrip()[2:])
            i += 1
            while i < len(lines):
                stripped = lines[i].strip()
                if not stripped or stripped == qualnames[qualnames.index(qn) + 1] \
                        if qn != qualnames[-1] and stripped == \
                        qualnames[(qualnames.index(qn) + 1) % len(qualnames)] \
                        else False:
                    break
                # Simpler: if the line is just another qualname, stop.
                if stripped in qualnames:
                    break
                block.append(stripped)
                i += 1
        result[qn] = " ".join(block).strip()
    return result


def extract_lean_statements(proof_file: Path,
                             qualnames: List[str]) -> Dict[str, str]:
    """Return {qualname: rendered_type_string} via `lake env lean` +
    `#check @<qualname>`.

    Appends the #check directives to a copy of the proof file (so the
    namespace context is correct) and runs lake env lean. Parses the
    one-line-per-check output.
    """
    body = proof_file.read_text()
    # A very wide format keeps each `#check` type on a single output line
    # (the default ~120-col width wraps long statements, which the
    # single-line parser below would otherwise truncate).
    check_lines = ["set_option format.width 100000"]
    check_lines += [f"#check @{qn}" for qn in qualnames]
    augmented = body + "\n" + "\n".join(check_lines) + "\n"
    with tempfile.NamedTemporaryFile(
        suffix=".lean", dir=str(proof_file.parent), delete=False, mode="w",
    ) as tf:
        tf.write(augmented)
        augmented_path = Path(tf.name)
    try:
        res = subprocess.run(
            ["lake", "env", "lean", augmented_path.name],
            cwd=str(proof_file.parent),
            capture_output=True, text=True, timeout=300,
        )
        stdout = res.stdout
    finally:
        try:
            augmented_path.unlink()
        except OSError:
            pass

    out_lines = stdout.splitlines()
    qn_set = set(qualnames)

    def _starts_new_check(line: str) -> bool:
        # A new `#check` block begins at column 0 with `<qualname> : ` or
        # `@<qualname> : ` for any cited qualname.
        s = line.strip()
        for q in qn_set:
            if s.startswith(q + " : ") or s.startswith(f"@{q} : "):
                return True
        return False

    result: Dict[str, str] = {}
    for qn in qualnames:
        for idx, line in enumerate(out_lines):
            line_stripped = line.strip()
            matched = None
            for prefix in (qn + " : ", f"@{qn} : "):
                if line_stripped.startswith(prefix):
                    matched = prefix
                    break
            if matched is None:
                continue
            # `#check` wraps long types across indented continuation
            # lines; gather them until the next check block / blank line.
            parts = [line_stripped[len(matched):]]
            j = idx + 1
            while j < len(out_lines):
                cont = out_lines[j]
                if not cont.strip():
                    break
                if _starts_new_check(cont):
                    break
                parts.append(cont.strip())
                j += 1
            result[qn] = " ".join(p for p in parts if p).strip()
            break
        result.setdefault(qn, "")
    return result
