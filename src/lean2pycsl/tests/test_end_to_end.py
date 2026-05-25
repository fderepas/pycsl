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
    with pytest.raises(KeyError, match="def 'ghost' not found"):
        run(config_path=cfg, no_check=True)


def _stage_fixture(fixture_dir: Path, work_dir: Path) -> None:
    """Copy fixture files into `work_dir` so writes don't pollute the
    source tree."""
    for name in ("spec.lean", "impl.py", "config.toml"):
        (work_dir / name).write_text((fixture_dir / name).read_text())
