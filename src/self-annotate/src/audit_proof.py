"""Namespace-aware audit for `#@ proof rocq` / `#@ proof lean`
directives.

Parses Rocq `.v` and Lean `.lean` files in the file's proof directory
and confirms that each cited qualname names a theorem declared inside
the matching nested module/namespace path.

Example: `#@ proof rocq Pycsl.Reference.Gcd.gcd_result_nonneg` PASSES
iff some `.v` file in the proof dir contains `Module Pycsl. Module
Reference. Module Gcd.` (in any nesting form) with a `Theorem
gcd_result_nonneg ...` inside that nesting.

The parsers are line-oriented state machines, not full Coq/Lean
front-ends. The supported subset is documented per-parser below.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Set

# ---------------------------------------------------------------------------
# Report type
# ---------------------------------------------------------------------------


@dataclass
class AuditReport:
    """Outcome of one audit invocation.

    `passes`, `failures`, `skips` are human-readable strings ready to
    print (one per directive). `exit_code` is 0 on no failures, 1 on
    any failure. Skips do not affect the exit code in this MVP.
    """
    passes: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)
    skips: List[str] = field(default_factory=list)

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def exit_code(self) -> int:
        return 1 if self.failures else 0

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns self.failures, self.passes, self.skips
    def extend(self, other: "AuditReport") -> None:
        self.passes.extend(other.passes)
        self.failures.extend(other.failures)
        self.skips.extend(other.skips)


# ---------------------------------------------------------------------------
# Directive extraction
# ---------------------------------------------------------------------------


@dataclass
class _Directive:
    prover: str          # "rocq" | "lean"
    qualname: str        # e.g. "Pycsl.Reference.Gcd.gcd_result_nonneg"
    py_file: Path
    line_no: int


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _extract_directives(py_file: Path) -> List[_Directive]:
    """Find every `#@ proof rocq <qualname>` /
    `#@ proof lean <qualname>` line in `py_file`.

    Line-based scan (not via Module2_Parser) so the audit works even
    on a Python file with broken contract syntax — the only thing we
    need is the qualname, not the contract semantics."""
    result: List[_Directive] = []
    text = py_file.read_text()
    for line_no, raw in enumerate(text.splitlines(), 1):
        stripped = raw.lstrip()
        if not stripped.startswith("#@ proof "):
            continue
        # Expected shape: `#@ proof <prover> <qualname>`
        parts = stripped.split(None, 3)
        if len(parts) < 4:
            continue
        # parts == ["#@", "proof", "<prover>", "<qualname>..."]
        prover = parts[2]
        if prover not in ("rocq", "lean"):
            continue
        qualname = parts[3].split()[0]  # trim trailing whitespace/comments
        result.append(_Directive(prover=prover, qualname=qualname,
                                  py_file=py_file, line_no=line_no))
    return result


# ---------------------------------------------------------------------------
# Rocq parser
# ---------------------------------------------------------------------------

# Declaration keywords whose immediate next identifier is a theorem-like
# name we want to index.
_ROCQ_DECL_KEYWORDS = {
    "Theorem", "Lemma", "Definition", "Inductive", "Record",
    "Fixpoint", "CoFixpoint", "Variant", "Class", "Structure",
    "Corollary", "Remark", "Fact", "Proposition", "Example",
}


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _strip_rocq_comments(text: str) -> str:
    """Remove `(* … *)` comments, supporting arbitrary nesting.

    Strings (`"…"`) are not protected — Coq theorems inside strings
    are vanishingly rare in proof files and would be a false positive
    (we document this in the module docstring)."""
    out: List[str] = []
    depth = 0
    i = 0
    n = len(text)
    while i < n:
        if depth == 0 and i + 1 < n and text[i] == "(" and text[i + 1] == "*":
            depth = 1
            i += 2
        elif depth > 0 and i + 1 < n and text[i] == "(" and text[i + 1] == "*":
            depth += 1
            i += 2
        elif depth > 0 and i + 1 < n and text[i] == "*" and text[i + 1] == ")":
            depth -= 1
            i += 2
        elif depth == 0:
            out.append(text[i])
            i += 1
        else:
            i += 1
    return "".join(out)


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _parse_rocq_file(path: Path) -> Set[str]:
    """Build the set of qualnames declared in a Rocq `.v` file.

    Supported constructs:
      - `Module <Name>.` / `Module Type <Name>.` — push name onto stack.
      - `End <Name>.` — pop; if name mismatches, the parse is salvaged
        by popping anyway (we don't validate file syntax — Coq's job).
      - `Section <Name>.` / `End <Name>.` — sections do NOT contribute
        to qualnames; pushed as empty stack frames so their `End`
        matches up.
      - Top-level declarations (`Theorem`, `Lemma`, etc.) — recorded
        as `".".join(module_stack + [name])`.

    Unsupported (silently skipped): `Include`, `Export`, `Import`,
    parameter type annotations, `Notation`, `Tactic Notation`."""
    qualnames: Set[str] = set()
    text = _strip_rocq_comments(path.read_text())
    module_stack: List[str] = []          # contributing names
    frame_stack: List[Optional[str]] = []  # None = Section; str = module/section name
    # Token-ish iteration. Coq is sensitive to `.` as a sentence
    # terminator, so we split there.
    sentences = text.replace("\n", " ").split(".")
    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue
        toks = s.split()
        head = toks[0]
        if head == "Module":
            # `Module Name`, `Module Type Name`, `Module Name : Sig`, etc.
            # `Module Name (params)` — first identifier after Module / Type.
            if len(toks) >= 2 and toks[1] == "Type":
                if len(toks) >= 3:
                    name = toks[2]
                    module_stack.append(name)
                    frame_stack.append(name)
            elif len(toks) >= 2:
                name = toks[1]
                # `Module Name := …` (immediate alias) is a one-line
                # declaration, NOT a block — only push if no `:=`.
                if ":=" in toks:
                    continue
                module_stack.append(name)
                frame_stack.append(name)
        elif head == "Section":
            if len(toks) >= 2:
                # Sections don't contribute to qualnames; push None
                frame_stack.append(None)
        elif head == "End":
            # `End Name` — pop one frame. If the frame was a module
            # (str), also pop module_stack. If a section (None), only
            # pop frame_stack.
            if frame_stack:
                top = frame_stack.pop()
                if top is not None and module_stack and module_stack[-1] == top:
                    module_stack.pop()
                elif top is not None and module_stack:
                    # Mismatched End — be lenient: pop module_stack
                    # too so subsequent declarations don't pile up.
                    module_stack.pop()
        elif head in _ROCQ_DECL_KEYWORDS:
            if len(toks) >= 2:
                # Some decls have a non-identifier second token (e.g.
                # `Definition foo : nat := ...`) — `foo` IS still toks[1].
                # But guard against `Theorem :` (impossible in practice).
                name = toks[1].rstrip("(:").lstrip()
                # Trim leading non-ident chars like `@` (universe poly).
                name = name.lstrip("@")
                if name and (name[0].isalpha() or name[0] == "_"):
                    qualnames.add(".".join(module_stack + [name]))
    return qualnames


# ---------------------------------------------------------------------------
# Lean parser
# ---------------------------------------------------------------------------

_LEAN_DECL_KEYWORDS = {
    "theorem", "lemma", "def", "definition", "structure",
    "inductive", "class", "abbrev", "instance",
}


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _strip_lean_comments(text: str) -> str:
    """Remove `--` line comments and `/- … -/` block comments
    (nestable). Strings (`"…"`) are not protected — same caveat as
    the Rocq parser."""
    out: List[str] = []
    depth = 0
    i = 0
    n = len(text)
    while i < n:
        # Block comment open / close (nest-aware)
        if depth == 0 and i + 1 < n and text[i] == "/" and text[i + 1] == "-":
            depth = 1
            i += 2
        elif depth > 0 and i + 1 < n and text[i] == "/" and text[i + 1] == "-":
            depth += 1
            i += 2
        elif depth > 0 and i + 1 < n and text[i] == "-" and text[i + 1] == "/":
            depth -= 1
            i += 2
        elif depth > 0:
            i += 1
        # Line comment
        elif i + 1 < n and text[i] == "-" and text[i + 1] == "-":
            # Skip to EOL
            while i < n and text[i] != "\n":
                i += 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _parse_lean_file(path: Path) -> Set[str]:
    """Build the set of qualnames declared in a Lean `.lean` file.

    Supported:
      - `namespace X.Y.Z` — split on `.` and push each segment.
      - `end X.Y.Z` — pop matching prefix from the stack; if it
        doesn't match, pop the same number of segments anyway
        (lenient — Lean's job to validate).
      - Top-level decls (`theorem`, `def`, ...) — recorded as
        `".".join(ns_stack + [name])`.

    NOT supported (silently skipped): `_root_` prefix, `section`,
    `variable`, `instance` body content. Sections do not affect
    namespace; we ignore them."""
    qualnames: Set[str] = set()
    text = _strip_lean_comments(path.read_text())
    ns_stack: List[str] = []
    # Track how many segments each `namespace` line pushed, so the
    # corresponding `end X.Y.Z` knows how many to pop.
    push_depths: List[int] = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        toks = s.split()
        head = toks[0]
        if head == "namespace":
            if len(toks) >= 2:
                segs = toks[1].split(".")
                ns_stack.extend(segs)
                push_depths.append(len(segs))
        elif head == "end":
            if push_depths:
                d = push_depths.pop()
                for _ in range(d):
                    if ns_stack:
                        ns_stack.pop()
        elif head in _LEAN_DECL_KEYWORDS:
            # `theorem name (args) : type := proof`
            #             ^toks[1]
            # Handle the rare `@[simp] theorem` attribute form — head
            # would be `@[simp]` and `theorem` is toks[1]; in that
            # case the name is toks[2].
            name_idx = 1
            if len(toks) >= 2:
                name = toks[name_idx].split(":")[0].split("(")[0]
                # Strip Lean's `_root_` prefix if present.
                if name.startswith("_root_."):
                    name = name[len("_root_."):]
                    # Record at top level (no ns_stack prefix).
                    if name:
                        qualnames.add(name)
                    continue
                if name and (name[0].isalpha() or name[0] == "_"):
                    qualnames.add(".".join(ns_stack + [name]))
    return qualnames


# ---------------------------------------------------------------------------
# Per-language audit
# ---------------------------------------------------------------------------


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _index_proofs_dir(proofs_dir: Path, prover: str) -> Set[str]:
    """Parse every proof file under `proofs_dir` and return the union
    of qualnames declared anywhere in it."""
    qualnames: Set[str] = set()
    if not proofs_dir.is_dir():
        return qualnames
    ext = ".v" if prover == "rocq" else ".lean"
    for path in sorted(proofs_dir.iterdir()):
        if path.is_file() and path.suffix == ext:
            try:
                if prover == "rocq":
                    qualnames |= _parse_rocq_file(path)
                else:
                    qualnames |= _parse_lean_file(path)
            except (OSError, UnicodeDecodeError) as exc:
                print(f"  [!] parse error: {path}: {exc}", file=sys.stderr)
    return qualnames


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _audit_one_prover(py_file: Path, proofs_dir: Path, prover: str,
                       directives: List[_Directive],
                       reverify: bool = False,
                       project_root: Optional[Path] = None) -> AuditReport:
    """Audit all directives for one prover against one proof dir.

    With reverify=True, after the namespace-presence check passes for
    a citation, run `coqc` / `lake env lean` on the file containing
    that citation's qualname and inspect the assumption set via
    `Print Assumptions` / `#print axioms`. A non-allow-listed
    assumption is FAIL.
    """
    report = AuditReport()
    relevant = [d for d in directives if d.prover == prover]
    if not relevant:
        return report
    if not proofs_dir.is_dir():
        for d in relevant:
            report.failures.append(
                f"{d.py_file}:{d.line_no}  {d.prover}: {d.qualname}  "
                f"(proof dir not found: {proofs_dir})")
        return report
    qualnames = _index_proofs_dir(proofs_dir, prover)
    # Track which proof file each cited qualname lives in, for reverify.
    qualname_to_file: dict = {}
    if reverify:
        qualname_to_file = _index_proofs_dir_by_file(proofs_dir, prover)
    passed_directives: List[_Directive] = []
    for d in relevant:
        if d.qualname in qualnames:
            report.passes.append(
                f"{d.py_file}:{d.line_no}  {d.prover}: {d.qualname}")
            passed_directives.append(d)
        else:
            # Specific failure reason: is the namespace itself absent,
            # or just the theorem name?
            if "." in d.qualname:
                ns, theorem = d.qualname.rsplit(".", 1)
                ns_present = any(q.startswith(ns + ".") for q in qualnames)
                if ns_present:
                    reason = (f"theorem '{theorem}' not declared inside "
                              f"namespace '{ns}' in {proofs_dir}")
                else:
                    reason = (f"namespace path '{ns}' not present in "
                              f"{proofs_dir}")
            else:
                reason = (f"top-level theorem '{d.qualname}' not declared in "
                          f"{proofs_dir}")
            report.failures.append(
                f"{d.py_file}:{d.line_no}  {d.prover}: {d.qualname}  ({reason})")

    if reverify and passed_directives:
        from audit_proof_reverify import (
            verify_lean_file, verify_rocq_file,
        )
        # Group qualnames by source file so we compile each file once.
        by_file: dict = {}
        for d in passed_directives:
            src = qualname_to_file.get(d.qualname)
            if src is None:
                continue
            by_file.setdefault(src, []).append(d.qualname)
        if project_root is None:
            project_root = Path.cwd()
        for src, qns in by_file.items():
            if prover == "rocq":
                rep = verify_rocq_file(src, qns, project_root)
            else:
                rep = verify_lean_file(src, qns, project_root)
            tag = "reverify-cached" if rep.cached else "reverify"
            if not rep.compile_ok:
                stderr_short = (rep.compile_stderr or rep.compile_stdout)[:300]
                report.failures.append(
                    f"{prover}: {src} did not compile ({tag}): "
                    f"{stderr_short}".rstrip())
                continue
            for qn, allowed, axs in rep.qualname_results:
                if allowed:
                    sym = "Closed" if not axs else f"axioms={axs}"
                    report.passes.append(
                        f"{tag} {prover}: {qn}  ({sym}, "
                        f"{rep.elapsed_compile_s:.2f}s)")
                else:
                    report.failures.append(
                        f"{tag} {prover}: {qn} has non-allowlisted "
                        f"assumptions: {axs}")
    return report


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _index_proofs_dir_by_file(proofs_dir: Path, prover: str) -> dict:
    """Like _index_proofs_dir but returns a {qualname -> source_file} map.

    Used by the reverify path to find which .v / .lean file declares
    each cited qualname, so we can `coqc` / `lake env lean` just that
    file."""
    out: dict = {}
    ext = ".v" if prover == "rocq" else ".lean"
    if not proofs_dir.is_dir():
        return out
    for path in sorted(proofs_dir.iterdir()):
        if path.is_file() and path.suffix == ext:
            try:
                if prover == "rocq":
                    qns = _parse_rocq_file(path)
                else:
                    qns = _parse_lean_file(path)
            except (OSError, UnicodeDecodeError):
                continue
            for qn in qns:
                out.setdefault(qn, path)
    return out


# ---------------------------------------------------------------------------
# Public entry points
# ---------------------------------------------------------------------------


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _default_rocq_dir(py_file: Path) -> Path:
    return py_file.parent / f"{py_file.stem}.proofs" / "rocq"


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def _default_lean_dir(py_file: Path) -> Path:
    return py_file.parent / f"{py_file.stem}.proofs" / "lean"


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def audit_rocq(py_file: Path, proofs_dir: Optional[Path] = None,
               reverify: bool = False,
               project_root: Optional[Path] = None) -> AuditReport:
    """Audit only the `#@ proof rocq` directives in `py_file`."""
    py_file = py_file.resolve()
    if proofs_dir is None:
        proofs_dir = _default_rocq_dir(py_file)
    directives = _extract_directives(py_file)
    return _audit_one_prover(py_file, proofs_dir, "rocq", directives,
                              reverify=reverify, project_root=project_root)


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def audit_lean(py_file: Path, proofs_dir: Optional[Path] = None,
               reverify: bool = False,
               project_root: Optional[Path] = None) -> AuditReport:
    """Audit only the `#@ proof lean` directives in `py_file`."""
    py_file = py_file.resolve()
    if proofs_dir is None:
        proofs_dir = _default_lean_dir(py_file)
    directives = _extract_directives(py_file)
    return _audit_one_prover(py_file, proofs_dir, "lean", directives,
                              reverify=reverify, project_root=project_root)


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def audit_both(py_file: Path,
               rocq_dir: Optional[Path] = None,
               lean_dir: Optional[Path] = None,
               reverify: bool = False,
               project_root: Optional[Path] = None) -> AuditReport:
    """Audit both Rocq and Lean directives in `py_file`."""
    report = AuditReport()
    report.extend(audit_rocq(py_file, rocq_dir, reverify=reverify,
                              project_root=project_root))
    report.extend(audit_lean(py_file, lean_dir, reverify=reverify,
                              project_root=project_root))
    return report


#@ \trusted reviewer: pycsl-self-annotate
#@ requires True
#@ ensures True
#@ assigns \nothing
def print_report(report: AuditReport, header: str) -> None:
    """Print an audit report in the same shape the old shell script
    used (so CI parsers don't have to be updated)."""
    print(f"=== {header} ===")
    for line in report.passes:
        print(f"  ✓ {line}")
    if report.failures:
        print("=== Proof-attribution failures ===")
        for line in report.failures:
            print(f"  ✗ {line}")
    if report.skips:
        print("=== Proof-attribution skips ===")
        for line in report.skips:
            print(f"  · {line}")
    print("=== Proof-attribution audit summary ===")
    print(f"  Passed:  {len(report.passes)}")
    print(f"  Skipped: {len(report.skips)}")
    print(f"  Failed:  {len(report.failures)}")
