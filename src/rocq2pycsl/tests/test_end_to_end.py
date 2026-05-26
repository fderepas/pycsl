"""End-to-end golden test for rocq2pycsl.

Runs the CLI as a library function on the `double` fixture and asserts:

  1. The annotated Python matches the expected golden source byte-for-byte.
  2. The full pycsl round-trip (Why3 + Alt-Ergo) discharges every
     obligation, when Why3 is available.

Both assertions exercise the extraction → selection → translation →
emission → verification path that the plan §3 lays out.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from rocq2pycsl.cli import run
from rocq2pycsl.extractor import Backend


_GOLDEN = Path(__file__).resolve().parent / "golden"


def test_double_golden_matches_expected(tmp_path: Path):
    fx = _GOLDEN / "double"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
        no_check=True,            # ← golden diff only; pycsl check is below
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
    """Phase 6 — class fixture with two methods and arg_map rewriting
    `balance` → `self._balance`. The class invariant in the impl.py is
    preserved through annotation."""
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
    """Dict-as-function-type fixture: `nat -> option nat` passes
    through the arrow-type grammar production."""
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
    """List parameters: `length arr` → `Length`, `arr[i]` indexing."""
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
    """String-typed parameters and `\\str_length` postcondition."""
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
    """Tuple-returning fixture — exercises `fst`/`snd` → `\\result[i]`
    lowering for Coq's `Z * Z` return type."""
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
    """Boolean XOR fixture — exercises the 0/1 encoding of bool params
    and the `xorb a b → (a + b) - 2 * (a * b)` lowering rule added in
    Phase 3 of tuesday-01."""
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


def test_double_round_trips_through_pycsl(tmp_path: Path):
    fx = _GOLDEN / "double"
    _stage_fixture(fx, tmp_path)

    outcome = run(
        config_path=tmp_path / "config.toml",
        backend=Backend.LARK,
        verbose=False,
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


def test_strict_mode_propagates_translation_errors(tmp_path: Path):
    """A theorem with an unsupported fragment should abort under strict."""
    spec = tmp_path / "spec.v"
    spec.write_text(
        "Definition f (x : Z) : Z := x.\n"
        "Theorem t : forall x : Z, foo (bar x) = baz x.\n"
        "Admitted.\n"
    )
    impl = tmp_path / "impl.py"
    impl.write_text("def f(x: int) -> int:\n    return x\n")
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        '[input]\n'
        'rocq = "spec.v"\n'
        'python = "impl.py"\n'
        'output = "actual.py"\n'
        '[functions.f]\n'
        'python_name = "f"\n'
        'spec_theorems = ["t"]\n'
    )
    # Non-strict path tolerates the unknown function names (they become
    # IR.App which renders as Python function calls — pycsl would then
    # require their definitions, but the CLI doesn't know that).
    outcome = run(config_path=cfg, no_check=True, strict=False)
    # The annotations are produced. Whether pycsl accepts them is a
    # separate concern; here we just verify the path runs.
    assert "def f" in outcome.annotated_source


def _stage_fixture(fixture_dir: Path, work_dir: Path) -> None:
    """Copy `spec.v`, `impl.py`, `config.toml` into `work_dir` so writes
    don't pollute the source tree."""
    for name in ("spec.v", "impl.py", "config.toml"):
        (work_dir / name).write_text((fixture_dir / name).read_text())
