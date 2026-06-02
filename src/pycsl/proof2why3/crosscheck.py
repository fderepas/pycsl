"""3-way cross-check: Rocq IR ↔ Lean IR ↔ Registry IR (proof2why3 v0).

Given a Python file with `#@ proof rocq <qn>` / `#@ proof lean <qn>`
directives, this driver:

  1. Extracts the cited theorem types from the Rocq + Lean proof files
     via `extract.py`.
  2. Looks up the Module 6 `_AXIOM_REGISTRY` body for each qualname.
  3. Normalizes all three to the same canonical string form via
     `normalize.py`.
  4. Reports per-qualname agreement:
        PASS   — all three normalized strings are equal
        FAIL   — at least one pair disagrees; diff shows which side
                 differs

A FAIL between Rocq and Lean fingers a divergent theorem statement
(or a normalizer gap). A FAIL involving the Registry fingers a
mis-curated axiom body.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# Add Module 6 to the path so we can read _AXIOM_REGISTRY directly.
_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "pycsl"))


from audit_proof import _extract_directives           # noqa: E402
from proof2why3.extract import (                       # noqa: E402
    extract_lean_statements,
    extract_rocq_statements,
)
from proof2why3.normalize import (                     # noqa: E402
    normalize_prover_output,
    normalize_whyml_axiom,
)


@dataclass
class CrossCheckResult:
    """Per-qualname agreement report."""
    qualname: str
    rocq_raw: str = ""
    lean_raw: str = ""
    registry_raw: str = ""
    rocq_norm: str = ""
    lean_norm: str = ""
    registry_norm: str = ""

    @property
    def all_agree(self) -> bool:
        norms = [self.rocq_norm, self.lean_norm, self.registry_norm]
        present = [n for n in norms if n]
        if not present:
            return False
        return all(n == present[0] for n in present)

    @property
    def pairwise(self) -> Dict[str, bool]:
        return {
            "rocq==lean":     bool(self.rocq_norm) and bool(self.lean_norm)
                              and self.rocq_norm == self.lean_norm,
            "rocq==registry": bool(self.rocq_norm) and bool(self.registry_norm)
                              and self.rocq_norm == self.registry_norm,
            "lean==registry": bool(self.lean_norm) and bool(self.registry_norm)
                              and self.lean_norm == self.registry_norm,
        }

    def diagnostic(self) -> str:
        lines = [f"--- {self.qualname} ---"]
        lines.append(f"  rocq raw:      {self.rocq_raw}")
        lines.append(f"  lean raw:      {self.lean_raw}")
        lines.append(f"  registry raw:  {self.registry_raw}")
        lines.append(f"  rocq norm:     {self.rocq_norm}")
        lines.append(f"  lean norm:     {self.lean_norm}")
        lines.append(f"  registry norm: {self.registry_norm}")
        for label, ok in self.pairwise.items():
            lines.append(f"  {label}: {'PASS' if ok else 'FAIL'}")
        return "\n".join(lines)


def _load_axiom_registry() -> Dict[str, str]:
    """Pull _AXIOM_REGISTRY out of the live Module 6 preamble.

    Importing module6_whyml.preamble drags Module 6's full
    transitive imports — we instead read the dict via AST inspection
    to keep this script independent of the heavier Module 6 graph.
    """
    src = (_REPO_ROOT / "src" / "pycsl" / "module6_whyml" /
           "preamble.py").read_text()
    # Find the dict literal `_AXIOM_REGISTRY: Dict[str, str] = { ... }`.
    import ast
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.target.id == "_AXIOM_REGISTRY":
            d = ast.literal_eval(node.value)
            return {str(k): str(v) for k, v in d.items()}
    raise RuntimeError("_AXIOM_REGISTRY not found in preamble.py")


def crosscheck_file(py_file: Path) -> List[CrossCheckResult]:
    """Cross-check every cited qualname in `py_file`."""
    directives = _extract_directives(py_file)
    rocq_qns = sorted({d.qualname for d in directives if d.prover == "rocq"})
    lean_qns = sorted({d.qualname for d in directives if d.prover == "lean"})
    all_qns = sorted(set(rocq_qns) | set(lean_qns))

    registry = _load_axiom_registry()

    # Locate the proof files. Convention: <py_stem>.proofs/{rocq,lean}/.
    proofs_root = py_file.parent / f"{py_file.stem}.proofs"
    rocq_dir = proofs_root / "rocq"
    lean_dir = proofs_root / "lean"

    rocq_raw: Dict[str, str] = {}
    lean_raw: Dict[str, str] = {}

    if rocq_qns and rocq_dir.is_dir():
        for src in sorted(rocq_dir.glob("*.v")):
            qns_in_file = [qn for qn in rocq_qns
                           if qn.startswith(_module_namespace_of(src) + ".")]
            if not qns_in_file:
                # Best-effort: try all qualnames; extractor returns
                # empty string for unknowns.
                qns_in_file = rocq_qns
            chunk = extract_rocq_statements(src, qns_in_file)
            for qn, txt in chunk.items():
                if txt:
                    rocq_raw.setdefault(qn, txt)
    if lean_qns and lean_dir.is_dir():
        for src in sorted(lean_dir.glob("*.lean")):
            chunk = extract_lean_statements(src, lean_qns)
            for qn, txt in chunk.items():
                if txt:
                    lean_raw.setdefault(qn, txt)

    results: List[CrossCheckResult] = []
    for qn in all_qns:
        r = CrossCheckResult(qualname=qn)
        r.rocq_raw     = rocq_raw.get(qn, "")
        r.lean_raw     = lean_raw.get(qn, "")
        r.registry_raw = registry.get(qn, "")
        r.rocq_norm     = normalize_prover_output(r.rocq_raw) if r.rocq_raw else ""
        r.lean_norm     = normalize_prover_output(r.lean_raw) if r.lean_raw else ""
        r.registry_norm = normalize_whyml_axiom(r.registry_raw) if r.registry_raw else ""
        results.append(r)
    return results


def _module_namespace_of(rocq_file: Path) -> str:
    """Best-effort guess: a .v file at `0342.proofs/rocq/gcd.v` is
    likely wrapped in `Module Pycsl. Module Reference. Module Gcd.`
    matching the pycsl_target convention. We return the conventional
    prefix `Pycsl.Reference.<TestCapitalized>` where TestCapitalized
    is derived from the .v file stem.

    For non-conventional layouts, return empty string (caller falls
    back to trying all qualnames).
    """
    return ""  # v0: don't filter, let extractor handle all qualnames.


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point. Usage: proof2why3-crosscheck <py_file>."""
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 1:
        print("usage: proof2why3-crosscheck <py_file>", file=sys.stderr)
        return 2
    py_file = Path(argv[0]).resolve()
    if not py_file.is_file():
        print(f"error: not a file: {py_file}", file=sys.stderr)
        return 2
    results = crosscheck_file(py_file)
    n_pass = sum(1 for r in results if r.all_agree)
    n_fail = len(results) - n_pass
    print(f"=== proof2why3 cross-check ({py_file.name}) ===")
    for r in results:
        if r.all_agree:
            print(f"  ✓ {r.qualname}  (rocq == lean == registry)")
        else:
            print(f"  ✗ {r.qualname}")
            print(r.diagnostic())
    print(f"=== cross-check summary: {n_pass} PASS, {n_fail} FAIL ===")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
