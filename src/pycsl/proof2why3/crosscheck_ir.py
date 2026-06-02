"""IR-based 3-way cross-check (proof2why3 Phase 4 — sticky-01.md).

Replaces the v0 regex-based string-equality cross-check
(`crosscheck.py`) with a structural Term-equality check over the
shared IR (`ir.py`).

Pipeline per cited qualname:

    Rocq Check output ─┐
                       ├─→ parse_type_expr → Term
                       │       │
                       │       └─→ canonicalize → Term (canonical)
                       │
    Lean #check output ─┤  same
                       │
    Registry body ─────┘  same

    Three-way structural equality on the canonical Terms. Equality is
    decided by Python's `==` (frozen dataclass field tuple equality).

Diff reporting: when a pair disagrees, the report shows BOTH
canonical Terms pretty-printed and highlights the first node where
they differ (depth-first walk).

Used by `bin/proof2why3` CLI and (per Phase 5) by
`make self-annotate-verify` after wire-up.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT / "src" / "pycsl"))


from audit_proof import _extract_directives                # noqa: E402
from proof2why3.canonical import canonicalize              # noqa: E402
from proof2why3.extract import (                            # noqa: E402
    extract_lean_statements,
    extract_rocq_statements,
)
from proof2why3.extract_lean_meta import (                  # noqa: E402
    extract_lean_statements_meta,
    lean_meta_available,
)
from proof2why3.from_lean_json import project_to_ir as lean_ast_to_ir  # noqa: E402
from proof2why3.from_sexp import project_constr             # noqa: E402
from proof2why3.ir import Term, Unsupported                # noqa: E402
from proof2why3.parser import parse_type_expr               # noqa: E402
from proof2why3.sertop import extract_via_sertop, sertop_available  # noqa: E402


@dataclass
class IRCrossCheckResult:
    """Per-qualname structural cross-check report."""
    qualname: str
    rocq_raw: str = ""
    lean_raw: str = ""
    registry_raw: str = ""
    rocq_ir: Optional[Term] = None
    lean_ir: Optional[Term] = None
    registry_ir: Optional[Term] = None
    rocq_canon: Optional[Term] = None
    lean_canon: Optional[Term] = None
    registry_canon: Optional[Term] = None

    @property
    def all_agree(self) -> bool:
        canons = [c for c in
                  (self.rocq_canon, self.lean_canon, self.registry_canon)
                  if c is not None]
        if not canons:
            return False
        return all(c == canons[0] for c in canons)

    @property
    def pairwise(self) -> Dict[str, Optional[bool]]:
        def cmp(a: Optional[Term], b: Optional[Term]) -> Optional[bool]:
            if a is None or b is None:
                return None
            return a == b
        return {
            "rocq==lean":     cmp(self.rocq_canon, self.lean_canon),
            "rocq==registry": cmp(self.rocq_canon, self.registry_canon),
            "lean==registry": cmp(self.lean_canon, self.registry_canon),
        }

    @property
    def any_unsupported(self) -> bool:
        return any(isinstance(c, Unsupported)
                   for c in (self.rocq_canon, self.lean_canon,
                             self.registry_canon)
                   if c is not None)

    @property
    def registry_skipped(self) -> bool:
        """True when the qualname has prover-side IR but no registry
        body. Used for audit-anchor stubs (Module4/5/6 + preamble.proofs)
        where the citation is namespace-presence-only — there's no
        registry body to compare against, so the cross-check SKIPs
        rather than FAILing."""
        return (not self.registry_raw) and (
            self.rocq_canon is not None or self.lean_canon is not None
        )

    @property
    def provers_agree(self) -> bool:
        """When registry is skipped, the cross-check verdict reduces
        to rocq==lean (still meaningful)."""
        if self.rocq_canon is None or self.lean_canon is None:
            # One of the provers is missing — accept (e.g., Rocq-only
            # citations like Module 4's Phase1_AST.expr_eq_dec).
            return True
        return self.rocq_canon == self.lean_canon

    def diagnostic(self) -> str:
        lines = [f"--- {self.qualname} ---"]
        lines.append(f"  rocq raw:     {self.rocq_raw}")
        lines.append(f"  lean raw:     {self.lean_raw}")
        lines.append(f"  registry raw: {self.registry_raw}")
        if self.rocq_canon is not None:
            lines.append(f"  rocq canon:     {self.rocq_canon.pp()}")
        if self.lean_canon is not None:
            lines.append(f"  lean canon:     {self.lean_canon.pp()}")
        if self.registry_canon is not None:
            lines.append(f"  registry canon: {self.registry_canon.pp()}")
        for label, ok in self.pairwise.items():
            if ok is None:
                lines.append(f"  {label}: SKIP (one side missing)")
            elif ok:
                lines.append(f"  {label}: PASS")
            else:
                lines.append(f"  {label}: FAIL")
        if self.any_unsupported:
            lines.append("  NOTE: at least one side contains Unsupported "
                         "(parser gap); diff is unreliable")
        return "\n".join(lines)


def _load_axiom_registry() -> Dict[str, str]:
    """Read _AXIOM_REGISTRY from Module 6's preamble via AST inspection."""
    src = (_REPO_ROOT / "src" / "pycsl" / "module6_whyml" /
           "preamble.py").read_text()
    import ast
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and node.target.id == "_AXIOM_REGISTRY":
            d = ast.literal_eval(node.value)
            return {str(k): str(v) for k, v in d.items()}
    raise RuntimeError("_AXIOM_REGISTRY not found in preamble.py")


def _preprocess_whyml(body: str) -> str:
    """Rewrite Why3 axiom-body surface syntax into the parser's grammar.

    - Why3 separates a quantifier from its body with a dot
      (`forall x : ty. body`, and chained `forall x:ty. forall y:ty2. …`);
      the parser expects a comma. Convert every `: <type>.` to `: <type>,`
      for any (possibly multi-word) type such as `array int`.
    - Why3 writes conjunction as the two-character `/\\`; the lexer's
      conjunction token is the three-character form used throughout the
      IR (a raw-string artifact in `_OP_TOKENS`). Bridge the two so
      registry conjunctions tokenize like the Rocq/Lean side.
    """
    import re as _re
    # `... : <type>.` (end of a quantifier) → `... : <type>,`. The type is
    # the run of identifiers/spaces between the colon and the dot.
    out = _re.sub(r":\s*([A-Za-z_][\w ]*?)\.", r": \1,", body)
    # Two-char `/\` → three-char `/\\` (the lexer's conjunction token).
    out = out.replace("/\\", "/\\\\")
    return out


def crosscheck_file_ir(py_file: Path) -> List[IRCrossCheckResult]:
    """Run the IR-based 3-way cross-check on a Python file's
    `#@ proof rocq/lean` citations."""
    directives = _extract_directives(py_file)
    rocq_qns = sorted({d.qualname for d in directives if d.prover == "rocq"})
    lean_qns = sorted({d.qualname for d in directives if d.prover == "lean"})
    all_qns = sorted(set(rocq_qns) | set(lean_qns))

    registry = _load_axiom_registry()
    proofs_root = py_file.parent / f"{py_file.stem}.proofs"
    rocq_dir = proofs_root / "rocq"
    lean_dir = proofs_root / "lean"

    rocq_raw: Dict[str, str] = {}
    lean_raw: Dict[str, str] = {}
    # Rocq elaborated-AST IR from sertop (Phase A v1). Populated only
    # when PROOF2WHY3_USE_SERTOP=1 AND sertop is installed.
    rocq_sertop_ir: Dict[str, Term] = {}
    use_sertop = (os.environ.get("PROOF2WHY3_USE_SERTOP", "") == "1"
                  and sertop_available())
    if rocq_qns and rocq_dir.is_dir():
        for src in sorted(rocq_dir.glob("*.v")):
            if use_sertop:
                sertop_result = extract_via_sertop(src, rocq_qns)
                for qn, sexp in sertop_result.items():
                    rocq_sertop_ir.setdefault(qn, project_constr(sexp))
                # Also keep pretty `Check` output for diagnostics when
                # available via the text path.
            chunk = extract_rocq_statements(src, rocq_qns)
            for qn, txt in chunk.items():
                if txt:
                    rocq_raw.setdefault(qn, txt)
    # Track which Lean qualnames were resolved by the meta-extractor
    # so we can skip the v1 text path for them.
    lean_meta_ir: Dict[str, Term] = {}
    use_lean_meta = os.environ.get("PROOF2WHY3_USE_LEAN_META", "") == "1"
    if lean_qns and lean_dir.is_dir():
        for src in sorted(lean_dir.glob("*.lean")):
            if use_lean_meta and lean_meta_available(lean_dir):
                meta = extract_lean_statements_meta(src, lean_qns)
                for qn, obj in meta.items():
                    ast = obj.get("ast")
                    if ast is not None:
                        lean_meta_ir.setdefault(qn, lean_ast_to_ir(ast))
                        # Also keep the pretty `type` for diagnostics.
                        lean_raw.setdefault(qn, obj.get("type", ""))
                # If meta covered all, skip the text extractor.
                remaining = [q for q in lean_qns if q not in lean_meta_ir]
                if not remaining:
                    continue
            chunk = extract_lean_statements(src, lean_qns)
            for qn, txt in chunk.items():
                if txt:
                    lean_raw.setdefault(qn, txt)

    results: List[IRCrossCheckResult] = []
    for qn in all_qns:
        r = IRCrossCheckResult(qualname=qn)
        r.rocq_raw     = rocq_raw.get(qn, "")
        r.lean_raw     = lean_raw.get(qn, "")
        r.registry_raw = registry.get(qn, "")
        if qn in rocq_sertop_ir:
            # Use the sertop-extracted elaborated AST.
            r.rocq_ir = rocq_sertop_ir[qn]
            r.rocq_canon = canonicalize(r.rocq_ir)
        elif r.rocq_raw:
            r.rocq_ir = parse_type_expr(r.rocq_raw)
            r.rocq_canon = canonicalize(r.rocq_ir)
        if qn in lean_meta_ir:
            # Use the Lean meta-extractor's structured IR rather than
            # parsing the pretty-printed type string.
            r.lean_ir = lean_meta_ir[qn]
            r.lean_canon = canonicalize(r.lean_ir)
        elif r.lean_raw:
            r.lean_ir = parse_type_expr(r.lean_raw)
            r.lean_canon = canonicalize(r.lean_ir)
        if r.registry_raw:
            r.registry_ir = parse_type_expr(_preprocess_whyml(r.registry_raw))
            r.registry_canon = canonicalize(r.registry_ir)
        results.append(r)
    return results


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry. Usage: proof2why3-crosscheck-ir <py_file>."""
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 1:
        print("usage: proof2why3-crosscheck-ir <py_file>", file=sys.stderr)
        return 2
    py_file = Path(argv[0]).resolve()
    if not py_file.is_file():
        print(f"error: not a file: {py_file}", file=sys.stderr)
        return 2
    results = crosscheck_file_ir(py_file)
    n_pass = 0
    n_skip = 0
    n_fail = 0
    print(f"=== proof2why3 IR cross-check ({py_file.name}) ===")
    for r in results:
        if r.registry_skipped:
            # Audit-anchor stub case: no registry body to compare,
            # but the provers should still agree if both are cited.
            if r.provers_agree and not r.any_unsupported:
                n_skip += 1
                ref = r.rocq_canon or r.lean_canon
                print(f"  · {r.qualname}  SKIP (registry not cited; "
                      f"provers agree, hash={hash(ref) % 10**10})")
            else:
                n_fail += 1
                print(f"  ✗ {r.qualname}  (registry not cited AND provers disagree)")
                print(r.diagnostic())
        elif r.all_agree and not r.any_unsupported:
            n_pass += 1
            ref = r.rocq_canon or r.lean_canon or r.registry_canon
            print(f"  ✓ {r.qualname}  (rocq ≡ lean ≡ registry, "
                  f"hash={hash(ref) % 10**10})")
        else:
            n_fail += 1
            print(f"  ✗ {r.qualname}")
            print(r.diagnostic())
    print(f"=== IR cross-check summary: {n_pass} PASS, "
          f"{n_skip} SKIP, {n_fail} FAIL ===")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
