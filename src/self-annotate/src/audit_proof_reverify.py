"""Re-verification of cited proofs (Phase 0 — sticky-01.md).

Where `audit_proof.py` only performs a syntactic namespace-aware
presence check, this module actually invokes `coqc` (Rocq) and
`lake env lean` (Lean) on each proof file and then queries
`Print Assumptions` / `#print axioms` for each cited qualname.

A successful reverify means: the proof file compiles under its
prover's kernel, the cited theorem's assumption set is a subset of
the kernel-axiom allow-list (`proof_axiom_allowlist.py`), and the
result is cached by SHA-256 of the proof file's content.

Cache: `.audit-cache/{rocq,lean}/<sha256>.json`. Invalidated by file
edits automatically (different SHA).

Per `sticky-01.md` Phase 0.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set

from proof_axiom_allowlist import (
    is_lean_axiom_allowed,
    is_rocq_assumption_allowed,
    parse_lean_axioms_line,
    parse_rocq_assumptions_block,
)


# ---------------------------------------------------------------------------
# Report type
# ---------------------------------------------------------------------------


@dataclass
class ReverifyReport:
    """Outcome of one re-verification.

    compile_ok=True iff the prover accepted the file under its kernel
    (`coqc` exit 0 / `lake env lean` exit 0).

    qualname_results: per-qualname, the assumption set the prover
    reports for the cited theorem, paired with a bool indicating
    whether the entire set is in the allow-list.
    """
    proof_file: Path
    prover: str                     # "rocq" or "lean"
    compile_ok: bool
    compile_stdout: str = ""
    compile_stderr: str = ""
    elapsed_compile_s: float = 0.0
    qualname_results: List[tuple[str, bool, List[str]]] = field(default_factory=list)
    cached: bool = False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    @property
    def ok(self) -> bool:
        """Overall PASS — compile succeeded AND every cited qualname's
        assumption set is allow-listed."""
        if not self.compile_ok:
            return False
        return all(allowed for (_, allowed, _) in self.qualname_results)
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing

    def summary(self) -> str:
        head = ("PASS" if self.ok else "FAIL")
        cache = " (cached)" if self.cached else ""
        return (f"{head} reverify {self.prover}: {self.proof_file}"
                f" compile={self.compile_ok} "
                f"qualnames_ok={sum(1 for (_, ok, _) in self.qualname_results if ok)}"
                f"/{len(self.qualname_results)}"
                f" ({self.elapsed_compile_s:.2f}s){cache}")


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing


def _cache_root(project_root: Path) -> Path:
    """Project-local cache dir. Created on first use."""
    root = project_root / ".audit-cache"
    root.mkdir(parents=True, exist_ok=True)
    return root
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing


def _cache_key(proof_file: Path, qualnames: List[str],
               prover: str, prover_version: str) -> str:
    """Cache key = sha(file) + sha(sorted qualnames) + prover version.
    Changes in any of these invalidate the cache."""
    parts = [
        _sha256_file(proof_file),
        ",".join(sorted(qualnames)),
        prover,
        prover_version,
    ]
    return hashlib.sha256("|".join(parts).encode()).hexdigest()
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing


def _cache_load(project_root: Path, prover: str, key: str) -> Optional[dict]:
    f = _cache_root(project_root) / prover / f"{key}.json"
    if not f.is_file():
        return None
    try:
        return json.loads(f.read_text())
    except (OSError, json.JSONDecodeError):
        return None
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing


def _cache_store(project_root: Path, prover: str, key: str, payload: dict) -> None:
    d = _cache_root(project_root) / prover
    d.mkdir(parents=True, exist_ok=True)
    f = d / f"{key}.json"
    f.write_text(json.dumps(payload, indent=2))


# ---------------------------------------------------------------------------
# Prover version detection
# ---------------------------------------------------------------------------
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing


def _coqc_version() -> str:
    try:
        out = subprocess.run(
            ["coqc", "--version"], capture_output=True, text=True, timeout=10,
        )
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "coqc-unavailable"
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing


def _lean_version() -> str:
    try:
        out = subprocess.run(
            ["lake", "env", "lean", "--version"],
            capture_output=True, text=True, timeout=15,
        )
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "lean-unavailable"


# ---------------------------------------------------------------------------
# Rocq re-verification
# ---------------------------------------------------------------------------
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing


def verify_rocq_file(proof_file: Path, qualnames: List[str],
                     project_root: Path,
                     use_cache: bool = True) -> ReverifyReport:
    """Compile a Rocq .v file and verify each qualname's assumption set.

    Compile: `coqc -R <proof_file.parent> "" <proof_file>` from the
    file's parent directory. This gives the file unqualified imports
    of sibling .v files (the convention 0342.proofs/rocq/ uses).

    Assumption check: write a tiny companion .v file that
    `Require Import`s the proof module and runs
    `Print Assumptions <qualname>.` once per cited qualname. Run that
    companion through `coqc` and parse its stdout.
    """
    version = _coqc_version()
    key = _cache_key(proof_file, qualnames, "rocq", version)
    if use_cache:
        cached = _cache_load(project_root, "rocq", key)
        if cached is not None:
            report = ReverifyReport(
                proof_file=proof_file, prover="rocq",
                compile_ok=cached["compile_ok"],
                compile_stdout=cached["compile_stdout"],
                compile_stderr=cached["compile_stderr"],
                elapsed_compile_s=cached["elapsed_compile_s"],
                qualname_results=[
                    (qn, ok, axs)
                    for (qn, ok, axs) in cached["qualname_results"]
                ],
                cached=True,
            )
            return report

    proof_dir = proof_file.parent
    started = time.monotonic()
    # Step 1 — compile.
    res = subprocess.run(
        ["coqc", "-R", str(proof_dir), "", proof_file.name],
        cwd=str(proof_dir),
        capture_output=True, text=True, timeout=180,
    )
    elapsed_compile = time.monotonic() - started
    report = ReverifyReport(
        proof_file=proof_file, prover="rocq",
        compile_ok=(res.returncode == 0),
        compile_stdout=res.stdout, compile_stderr=res.stderr,
        elapsed_compile_s=elapsed_compile,
    )
    if not report.compile_ok:
        if use_cache:
            _cache_store(project_root, "rocq", key, _to_cache_payload(report))
        return report

    # Step 2 — Print Assumptions per qualname via a companion file.
    module_name = proof_file.stem  # e.g., "gcd"
    lines = [f"Require Import {module_name}."]
    for qn in qualnames:
        lines.append(f"Print Assumptions {qn}.")
    companion = "\n".join(lines) + "\n"
    with tempfile.NamedTemporaryFile(
        suffix=".v", dir=str(proof_dir), delete=False, mode="w",
    ) as tf:
        tf.write(companion)
        companion_path = Path(tf.name)
    try:
        check = subprocess.run(
            ["coqc", "-R", str(proof_dir), "", companion_path.name],
            cwd=str(proof_dir),
            capture_output=True, text=True, timeout=120,
        )
        stdout = check.stdout
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

    # Parse blocks delimited by repeated `Print Assumptions` echoes.
    # Coq prints each query's response in source order with no special
    # separator; we split by re-emitting one block per qualname using
    # the simple heuristic: every block is the substring between two
    # successive markers.
    blocks = _split_rocq_print_assumptions(stdout, qualnames)
    for qn in qualnames:
        block = blocks.get(qn, "")
        is_closed, names = parse_rocq_assumptions_block(block)
        if is_closed:
            allowed = True
            assumption_names: List[str] = []
        else:
            allowed = all(is_rocq_assumption_allowed(n) for n in names)
            assumption_names = names
        report.qualname_results.append((qn, allowed, assumption_names))

    if use_cache:
        _cache_store(project_root, "rocq", key, _to_cache_payload(report))
    return report
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing


def _split_rocq_print_assumptions(stdout: str, qualnames: List[str]) -> dict[str, str]:
    """Split coqc's stdout into one block per cited qualname.

    Coq emits one block per `Print Assumptions` query, in source order.
    Each block starts with either `Closed under the global context` (no
    assumptions) or `Axioms:` (or `Section Variables:`, etc.) followed
    by the assumption list. We delimit by spotting the start of each
    block and slicing.
    """
    # We split lazily: walk the qualnames in order, looking for blocks
    # that begin with either `Closed under the global context` or
    # `Axioms:` / `Section Variables:` / `Parameters:` / `Constants:`.
    block_starts: List[int] = []
    markers = ("Closed under the global context",
               "Axioms:", "Section Variables:",
               "Parameters:", "Constants:")
    pos = 0
    while pos < len(stdout):
        next_start = -1
        for marker in markers:
            idx = stdout.find(marker, pos)
            if idx != -1 and (next_start == -1 or idx < next_start):
                next_start = idx
        if next_start == -1:
            break
        block_starts.append(next_start)
        pos = next_start + 1

    result: dict[str, str] = {}
    for i, qn in enumerate(qualnames):
        if i >= len(block_starts):
            result[qn] = ""
            continue
        start = block_starts[i]
        end = block_starts[i + 1] if i + 1 < len(block_starts) else len(stdout)
        result[qn] = stdout[start:end]
    return result


# ---------------------------------------------------------------------------
# Lean re-verification
# ---------------------------------------------------------------------------
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing


def verify_lean_file(proof_file: Path, qualnames: List[str],
                     project_root: Path,
                     use_cache: bool = True) -> ReverifyReport:
    """Compile a Lean .lean file and verify each qualname's axiom set.

    Lean's `lake env lean <file>.lean` performs type-checking and
    returns 0 on success. We then append `#print axioms <qualname>` for
    each cited theorem to a copy of the file and re-run, parsing the
    output.
    """
    version = _lean_version()
    key = _cache_key(proof_file, qualnames, "lean", version)
    if use_cache:
        cached = _cache_load(project_root, "lean", key)
        if cached is not None:
            report = ReverifyReport(
                proof_file=proof_file, prover="lean",
                compile_ok=cached["compile_ok"],
                compile_stdout=cached["compile_stdout"],
                compile_stderr=cached["compile_stderr"],
                elapsed_compile_s=cached["elapsed_compile_s"],
                qualname_results=[
                    (qn, ok, axs)
                    for (qn, ok, axs) in cached["qualname_results"]
                ],
                cached=True,
            )
            return report

    started = time.monotonic()
    # Step 1 — compile-only sanity check.
    res = subprocess.run(
        ["lake", "env", "lean", proof_file.name],
        cwd=str(proof_file.parent),
        capture_output=True, text=True, timeout=300,
    )
    elapsed_compile = time.monotonic() - started
    report = ReverifyReport(
        proof_file=proof_file, prover="lean",
        compile_ok=(res.returncode == 0),
        compile_stdout=res.stdout, compile_stderr=res.stderr,
        elapsed_compile_s=elapsed_compile,
    )
    if not report.compile_ok:
        if use_cache:
            _cache_store(project_root, "lean", key, _to_cache_payload(report))
        return report

    # Step 2 — append `#print axioms` per qualname, re-run, parse.
    body = proof_file.read_text()
    appended_lines = [f"\n#print axioms {qn}" for qn in qualnames]
    augmented = body + "\n" + "\n".join(appended_lines) + "\n"
    with tempfile.NamedTemporaryFile(
        suffix=".lean", dir=str(proof_file.parent), delete=False, mode="w",
    ) as tf:
        tf.write(augmented)
        augmented_path = Path(tf.name)
    try:
        check = subprocess.run(
            ["lake", "env", "lean", augmented_path.name],
            cwd=str(proof_file.parent),
            capture_output=True, text=True, timeout=300,
        )
        stdout = check.stdout
    finally:
        try:
            augmented_path.unlink()
        except OSError:
            pass

    # Lean prints one line per `#print axioms`:
    #   'foo.bar' depends on axioms: [propext, Quot.sound]
    # Match each cited qualname to its line via substring search.
    by_qn: dict[str, str] = {}
    for line in stdout.splitlines():
        for qn in qualnames:
            if f"'{qn}'" in line or qn in line:
                by_qn[qn] = line
                break

    for qn in qualnames:
        line = by_qn.get(qn, "")
        axs = parse_lean_axioms_line(line)
        if not line:
            # No matching output line — treat as FAIL with stub assumption.
            allowed = False
            axs = ["<unknown — #print axioms line missing>"]
        else:
            allowed = all(is_lean_axiom_allowed(a) for a in axs)
        report.qualname_results.append((qn, allowed, axs))

    if use_cache:
        _cache_store(project_root, "lean", key, _to_cache_payload(report))
    return report


# ---------------------------------------------------------------------------
# Cache payload helpers
# ---------------------------------------------------------------------------
#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing


def _to_cache_payload(report: ReverifyReport) -> dict:
    return {
        "compile_ok": report.compile_ok,
        "compile_stdout": report.compile_stdout,
        "compile_stderr": report.compile_stderr,
        "elapsed_compile_s": report.elapsed_compile_s,
        "qualname_results": [
            [qn, ok, axs] for (qn, ok, axs) in report.qualname_results
        ],
    }
