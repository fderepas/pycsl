"""End-to-end golden test for lean2pycsl.

Runs the CLI as a library function on the `double` fixture and asserts:

  1. The annotated Python matches the expected golden source exactly.
  2. The annotated source is *identical* to what rocq2pycsl produces
     from its parallel fixture — this is the foundation pycsl_bridge
     will stand on.
  3. The full pycsl round-trip (Why3 + Alt-Ergo) discharges every
     obligation, when Why3 is available.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from lean2pycsl.cli import run
from lean2pycsl.extractor import Backend


_GOLDEN = Path(__file__).resolve().parent / "golden"
_ROCQ_GOLDEN = Path(__file__).resolve().parents[2] / "rocq2pycsl" / "tests" / "golden"


def test_double_golden_matches_expected(tmp_path: Path):
    fx = _GOLDEN / "double"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
        no_check=True,
        verbose=False,
    )

    actual = outcome.annotated_source
    expected = (fx / "expected.py").read_text()
    assert actual == expected, (
        "annotated output drift:\n"
        f"--- expected ---\n{expected}\n"
        f"--- actual ---\n{actual}\n"
    )


def test_bank_account_golden_matches_expected(tmp_path: Path):
    """Phase 6 — Lean class fixture mirroring the Rocq bank_account."""
    fx = _GOLDEN / "bank_account"
    _stage_fixture(fx, tmp_path)
    outcome = run(config_path=tmp_path / "config.toml", backend=Backend.LARK, no_check=True)
    assert outcome.annotated_source == (fx / "expected.py").read_text()


def test_array_fill_zero_golden_matches_expected(tmp_path: Path):
    fx = _GOLDEN / "array_fill_zero"
    _stage_fixture(fx, tmp_path)
    outcome = run(config_path=tmp_path / "config.toml", backend=Backend.LARK, no_check=True)
    assert outcome.annotated_source == (fx / "expected.py").read_text()


def test_list_length_after_append_golden_matches_expected(tmp_path: Path):
    fx = _GOLDEN / "list_length_after_append"
    _stage_fixture(fx, tmp_path)
    outcome = run(config_path=tmp_path / "config.toml", backend=Backend.LARK, no_check=True)
    assert outcome.annotated_source == (fx / "expected.py").read_text()


def test_set_union_eq_golden_matches_expected(tmp_path: Path):
    fx = _GOLDEN / "set_union_eq"
    _stage_fixture(fx, tmp_path)
    outcome = run(config_path=tmp_path / "config.toml", backend=Backend.LARK, no_check=True)
    assert outcome.annotated_source == (fx / "expected.py").read_text()


def test_dict_insert_lookup_golden_matches_expected(tmp_path: Path):
    """Lean dict-as-function fixture, mirroring the Rocq dict_insert_lookup."""
    fx = _GOLDEN / "dict_insert_lookup"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
        no_check=True,
    )
    actual = outcome.annotated_source
    expected = (fx / "expected.py").read_text()
    assert actual == expected


def test_array_sum_nonneg_golden_matches_expected(tmp_path: Path):
    """Lean List parameters: `List.length arr` → `Length`. Mirrors the
    Rocq array_sum_nonneg fixture."""
    fx = _GOLDEN / "array_sum_nonneg"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
        no_check=True,
    )
    actual = outcome.annotated_source
    expected = (fx / "expected.py").read_text()
    assert actual == expected


def test_concat_length_golden_matches_expected(tmp_path: Path):
    """String fixture: `s.length` dot syntax + `String.length` both
    lower to `StrLength`."""
    fx = _GOLDEN / "concat_length"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
        no_check=True,
    )
    actual = outcome.annotated_source
    expected = (fx / "expected.py").read_text()
    assert actual == expected


def test_divmod_pair_golden_matches_expected(tmp_path: Path):
    """Tuple-returning fixture mirroring the Rocq divmod_pair. Lean's
    `(divmod_pair a b).fst` dot-syntax exercises the postfix_atom
    grammar production and `_METHOD_TO_FUNCTION` rewrite."""
    fx = _GOLDEN / "divmod_pair"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
        no_check=True,
        verbose=False,
    )

    actual = outcome.annotated_source
    expected = (fx / "expected.py").read_text()
    assert actual == expected, (
        "annotated output drift:\n"
        f"--- expected ---\n{expected}\n"
        f"--- actual ---\n{actual}\n"
    )


def test_bool_xor_golden_matches_expected(tmp_path: Path):
    """Lean Bool XOR fixture — paired with the Rocq bool_xor fixture to
    demonstrate cross-prover convergence on the same PyCSL contract."""
    fx = _GOLDEN / "bool_xor"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
        no_check=True,
        verbose=False,
    )

    actual = outcome.annotated_source
    expected = (fx / "expected.py").read_text()
    assert actual == expected, (
        "annotated output drift:\n"
        f"--- expected ---\n{expected}\n"
        f"--- actual ---\n{actual}\n"
    )


def test_bool_xor_lean_and_rocq_produce_identical_output(tmp_path: Path):
    """Lean and Rocq versions of bool_xor must produce byte-identical
    annotated Python — the cross-prover convergence guarantee."""
    fx = _GOLDEN / "bool_xor"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
        no_check=True,
    )
    rocq_expected = (_ROCQ_GOLDEN / "bool_xor" / "expected.py").read_text()
    assert outcome.annotated_source == rocq_expected


def test_double_produces_same_output_as_rocq2pycsl_pipeline(tmp_path: Path):
    """The whole point of the parallel architecture: the same logical
    spec, formalized in Rocq AND in Lean, should produce the same
    annotated Python."""
    fx = _GOLDEN / "double"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
        no_check=True,
    )

    rocq_expected_path = _ROCQ_GOLDEN / "double" / "expected.py"
    if not rocq_expected_path.exists():
        pytest.skip("rocq2pycsl golden fixture absent")
    rocq_expected = rocq_expected_path.read_text()
    assert outcome.annotated_source == rocq_expected, (
        "lean2pycsl and rocq2pycsl produced different annotations — the "
        "pycsl_bridge canonicalizer will diverge on this case."
    )


def test_double_round_trips_through_pycsl(tmp_path: Path):
    fx = _GOLDEN / "double"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
    )

    verdict = outcome.verdict
    assert verdict is not None
    if "why3" in verdict.stdout.lower() and "not found" in verdict.stdout.lower():
        pytest.skip("why3 not installed")
    assert verdict.exit_code == 0, (
        f"pycsl exited {verdict.exit_code}\n"
        f"--- annotated ---\n{outcome.annotated_source}\n"
        f"--- stdout ---\n{verdict.stdout}\n"
        f"--- stderr ---\n{verdict.stderr}"
    )
    assert verdict.all_valid, verdict.summary()


def test_dry_run_does_not_write_output(tmp_path: Path):
    fx = _GOLDEN / "double"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
        dry_run=True,
    )
    assert outcome.verdict is None
    assert not outcome.annotated_path.exists()


def test_missing_function_in_lean_raises(tmp_path: Path):
    spec = tmp_path / "spec.lean"
    spec.write_text(
        '@[pycsl_spec "ghost"] '
        'theorem t : ∀ (x : Nat), x = x := sorry\n'
    )
    impl = tmp_path / "impl.py"
    impl.write_text("def ghost(x: int) -> int:\n    return x\n")
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        '[input]\n'
        'lean = "spec.lean"\n'
        'python = "impl.py"\n'
        'output = "actual.py"\n'
        '[functions.ghost]\n'
        'python_name = "ghost"\n'
    )
    with pytest.raises(KeyError, match=r"def 'ghost'.* not found"):
        run(config_path=cfg, no_check=True)


def _stage_fixture(fixture_dir: Path, work_dir: Path) -> None:
    """Copy fixture files into `work_dir` so writes don't pollute the
    source tree."""
    for name in ("spec.lean", "impl.py", "config.toml"):
        (work_dir / name).write_text((fixture_dir / name).read_text())
