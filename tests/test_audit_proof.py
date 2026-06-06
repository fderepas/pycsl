"""Tests for `pycsl --audit-proof` and the underlying parsers."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Make src/pycsl importable.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "pycsl"))

from audit_proof import (  # noqa: E402
    _parse_rocq_file,
    _parse_lean_file,
    audit_rocq,
    audit_lean,
    audit_both,
)


# ---------------------------------------------------------------------------
# Rocq parser unit tests
# ---------------------------------------------------------------------------


def _write_v(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content)
    return p


def test_rocq_nested_module(tmp_path: Path) -> None:
    """Nested `Module A. Module B.` produces dotted qualnames."""
    f = _write_v(tmp_path, "x.v",
                 "Module A.\nModule B.\nTheorem t : True. Proof. trivial. Qed.\n"
                 "End B.\nEnd A.\n")
    assert _parse_rocq_file(f) == {"A.B.t"}


def test_rocq_dotted_module_via_sentence(tmp_path: Path) -> None:
    """`Module A. Module B. Module C.` on one line still nests correctly."""
    f = _write_v(tmp_path, "x.v",
                 "Module A. Module B. Module C.\n"
                 "Theorem t : True. Proof. trivial. Qed.\n"
                 "End C. End B. End A.\n")
    assert _parse_rocq_file(f) == {"A.B.C.t"}


def test_rocq_bare_top_level_theorem(tmp_path: Path) -> None:
    """Top-level `Theorem` (no Module) gets a bare qualname."""
    f = _write_v(tmp_path, "x.v", "Theorem foo : True. Proof. trivial. Qed.\n")
    assert "foo" in _parse_rocq_file(f)


def test_rocq_comment_with_theorem(tmp_path: Path) -> None:
    """A `Theorem` inside a comment is NOT recorded."""
    f = _write_v(tmp_path, "x.v",
                 "(* this comment mentions Theorem fake : True. *)\n"
                 "Theorem real : True. Proof. trivial. Qed.\n")
    qs = _parse_rocq_file(f)
    assert "real" in qs
    assert "fake" not in qs


def test_rocq_nested_comment(tmp_path: Path) -> None:
    """Nested `(* (* … *) *)` comments are skipped wholesale."""
    f = _write_v(tmp_path, "x.v",
                 "(* outer (* inner Theorem fake. *) still inside *)\n"
                 "Theorem real : True. Proof. trivial. Qed.\n")
    assert _parse_rocq_file(f) == {"real"}


def test_rocq_section_does_not_contribute(tmp_path: Path) -> None:
    """`Section` blocks do not contribute to the qualname."""
    f = _write_v(tmp_path, "x.v",
                 "Module A.\nSection S.\n"
                 "Theorem t : True. Proof. trivial. Qed.\n"
                 "End S.\nEnd A.\n")
    assert _parse_rocq_file(f) == {"A.t"}


def test_rocq_multiple_keywords(tmp_path: Path) -> None:
    """Definition, Lemma, Inductive all recognised."""
    f = _write_v(tmp_path, "x.v",
                 "Module M.\n"
                 "Definition d := 0.\n"
                 "Lemma l : True. Proof. trivial. Qed.\n"
                 "Inductive ind := | C.\n"
                 "End M.\n")
    qs = _parse_rocq_file(f)
    assert qs == {"M.d", "M.l", "M.ind"}


# ---------------------------------------------------------------------------
# Lean parser unit tests
# ---------------------------------------------------------------------------


def _write_lean(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content)
    return p


def test_lean_dotted_namespace(tmp_path: Path) -> None:
    """`namespace A.B.C` splits into three segments."""
    f = _write_lean(tmp_path, "x.lean",
                    "namespace A.B.C\ntheorem t : True := trivial\nend A.B.C\n")
    assert _parse_lean_file(f) == {"A.B.C.t"}


def test_lean_nested_namespace(tmp_path: Path) -> None:
    """`namespace A / namespace B` (separate lines) nests."""
    f = _write_lean(tmp_path, "x.lean",
                    "namespace A\nnamespace B\n"
                    "theorem t : True := trivial\n"
                    "end B\nend A\n")
    assert _parse_lean_file(f) == {"A.B.t"}


def test_lean_comment_line(tmp_path: Path) -> None:
    """`--` line comment is skipped."""
    f = _write_lean(tmp_path, "x.lean",
                    "-- theorem fake : True := trivial\n"
                    "theorem real : True := trivial\n")
    assert _parse_lean_file(f) == {"real"}


def test_lean_block_comment_nested(tmp_path: Path) -> None:
    """`/- /- inner -/ outer -/` block comments are skipped."""
    f = _write_lean(tmp_path, "x.lean",
                    "/- outer /- inner theorem fake -/ still in -/\n"
                    "theorem real : True := trivial\n")
    assert _parse_lean_file(f) == {"real"}


def test_lean_def_and_theorem(tmp_path: Path) -> None:
    """`def`, `theorem`, `lemma` all recognised."""
    f = _write_lean(tmp_path, "x.lean",
                    "namespace N\n"
                    "def f (x : Nat) : Nat := x\n"
                    "theorem t : True := trivial\n"
                    "lemma l : True := trivial\n"
                    "end N\n")
    assert _parse_lean_file(f) == {"N.f", "N.t", "N.l"}


# ---------------------------------------------------------------------------
# End-to-end audit tests
# ---------------------------------------------------------------------------


def test_audit_0342_passes() -> None:
    """The shipped 0342.py + 0342.proofs/ should produce 14 PASS / 0 FAIL."""
    py = ROOT / "test-suite" / "corpus" / "pycsl-reference" / "0342.py"
    report = audit_both(py)
    assert len(report.passes) == 14
    assert len(report.failures) == 0
    assert report.exit_code == 0


def test_audit_rocq_only_yields_seven() -> None:
    py = ROOT / "test-suite" / "corpus" / "pycsl-reference" / "0342.py"
    report = audit_rocq(py)
    assert len(report.passes) == 7
    assert len(report.failures) == 0


def test_audit_lean_only_yields_seven() -> None:
    py = ROOT / "test-suite" / "corpus" / "pycsl-reference" / "0342.py"
    report = audit_lean(py)
    assert len(report.passes) == 7
    assert len(report.failures) == 0


def test_audit_namespace_mismatch_fails(tmp_path: Path) -> None:
    """If the theorem exists in the dir but outside the cited namespace,
    the audit FAILS with a 'namespace path not present' message."""
    py = tmp_path / "test.py"
    py.write_text(
        "#@ proof rocq Pycsl.Reference.Gcd.gcd_result_nonneg\n"
        "def f() -> int: return 0\n")
    proofs = tmp_path / "test.proofs" / "rocq"
    proofs.mkdir(parents=True)
    (proofs / "bad.v").write_text(
        "Theorem gcd_result_nonneg : True. Proof. trivial. Qed.\n")
    report = audit_rocq(py)
    assert len(report.passes) == 0
    assert len(report.failures) == 1
    assert "namespace path 'Pycsl.Reference.Gcd' not present" in report.failures[0]


def test_audit_theorem_missing_in_namespace(tmp_path: Path) -> None:
    """Namespace exists but the cited theorem is absent → specific
    'theorem not declared inside namespace' message."""
    py = tmp_path / "test.py"
    py.write_text(
        "#@ proof rocq A.B.missing_thm\n"
        "def f() -> int: return 0\n")
    proofs = tmp_path / "test.proofs" / "rocq"
    proofs.mkdir(parents=True)
    (proofs / "x.v").write_text(
        "Module A. Module B.\n"
        "Theorem present : True. Proof. trivial. Qed.\n"
        "End B. End A.\n")
    report = audit_rocq(py)
    assert len(report.failures) == 1
    assert "theorem 'missing_thm' not declared inside namespace 'A.B'" in \
           report.failures[0]


def test_audit_missing_proof_dir_with_directives_fails(tmp_path: Path) -> None:
    """If a directive cites a prover but the proof dir doesn't exist,
    that's a hard FAIL (not a SKIP)."""
    py = tmp_path / "test.py"
    py.write_text(
        "#@ proof lean A.B.thm\n"
        "def f() -> int: return 0\n")
    # No proofs/ at all.
    report = audit_lean(py)
    assert len(report.failures) == 1
    assert "proof dir not found" in report.failures[0]


def test_audit_no_directives_is_clean(tmp_path: Path) -> None:
    """A Python file with no #@ proof directives produces an
    empty (passing) report, regardless of proof-dir presence."""
    py = tmp_path / "test.py"
    py.write_text("def f() -> int: return 0\n")
    report = audit_both(py)
    assert len(report.passes) == 0
    assert len(report.failures) == 0
    assert report.exit_code == 0


def test_audit_override_rocq_proofs_path(tmp_path: Path) -> None:
    """--rocq-proofs-path override uses the supplied dir."""
    py = tmp_path / "test.py"
    py.write_text("#@ proof rocq M.t\ndef f() -> int: return 0\n")
    custom = tmp_path / "elsewhere" / "rocq"
    custom.mkdir(parents=True)
    (custom / "x.v").write_text(
        "Module M.\nTheorem t : True. Proof. trivial. Qed.\nEnd M.\n")
    report = audit_rocq(py, proofs_dir=custom)
    assert len(report.passes) == 1
    assert len(report.failures) == 0
