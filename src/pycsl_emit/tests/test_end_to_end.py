"""Phase A acceptance gate.

Build an IR by hand, run it through the translator, insert the result
onto a Python source via the emitter, invoke pycsl through the checker,
and assert the verdict. This is the end-to-end smoke test that proves
the four shared-backend modules cooperate.

Two cases:

  1. `add_one` — trivial postcondition `\\result == x + 1`. The full
     proof should discharge under any prover Why3 has available.

  2. `double_is_even` — exercises `Divides` in operational form
     (`\\result % 2 == 0`). Same expectation.

If Why3 is unavailable in the test environment, the tests fall back to
the `--no-proof` mode to confirm the pipeline at least produces valid
PyCSL syntax that the front end accepts.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from pycsl_emit.checker import ObligationStatus, run_pycsl
from pycsl_emit.emitter import annotate_source
from pycsl_emit.ir import App, BinOp, Divides, Lit, Result, Var
from pycsl_emit.translator import DividesStyle, NameMap, render
from pycsl_emit.translator.render import render_lines


def _run_pipeline_or_skip(annotated_path: Path, expected_count: int):
    """Run pycsl on `annotated_path`. If Why3 isn't installed, fall back
    to --no-proof and verify the syntax/transpile path."""
    v = run_pycsl(annotated_path)
    if "why3" in v.stdout.lower() and "not found" in v.stdout.lower():
        v_np = run_pycsl(annotated_path, no_proof=True)
        assert v_np.exit_code == 0, (
            f"--no-proof failed:\nSTDOUT:\n{v_np.stdout}\nSTDERR:\n{v_np.stderr}"
        )
        pytest.skip("why3 not installed; --no-proof path verified instead")
    return v


def test_phase_a_end_to_end_add_one(tmp_path: Path):
    """Pipeline: IR → render → emit → pycsl → verdict.

    Spec: \\result == x + 1
    """
    # 1. Build the IR by hand.
    ir_postcondition = BinOp(
        "==", Result(), BinOp("+", Var("x"), Lit(1)),
    )
    ir_precondition = BinOp(">=", Var("x"), Lit(0))

    # 2. Render to PyCSL surface.
    annotations = [
        f"requires {render(ir_precondition)}",
        f"ensures {render(ir_postcondition)}",
        "assigns \\nothing",
    ]
    assert annotations[0] == "requires x >= 0"
    assert annotations[1] == "ensures \\result == (x + 1)"

    # 3. Emit onto a hand-ported Python source.
    src = "def add_one(x: int) -> int:\n    return x + 1\n"
    annotated = annotate_source(src, "add_one", annotations)
    target = tmp_path / "add_one.annotated.py"
    target.write_text(annotated)

    # 4. Invoke pycsl + parse verdict.
    v = _run_pipeline_or_skip(target, expected_count=1)

    # 5. Assert.
    assert v.exit_code == 0, (
        f"pycsl failed:\n"
        f"--- file ---\n{annotated}\n"
        f"--- stdout ---\n{v.stdout}\n"
        f"--- stderr ---\n{v.stderr}"
    )
    assert v.total >= 1, f"no obligations parsed; output:\n{v.stdout}"
    assert v.all_valid, v.summary()
    for obs in v.obligations:
        assert obs.status is ObligationStatus.VALID


def test_phase_a_end_to_end_double_is_even(tmp_path: Path):
    """Exercises Divides in operational form.

    Spec: \\result == x * 2 and \\result is divisible by 2.
    """
    nm = NameMap.identity()

    # Two postconditions on `double(x) = x * 2`:
    #   1. \result == x * 2
    #   2. 2 | \result   →   \result % 2 == 0  (operational style)
    post_equal = BinOp("==", Result(), BinOp("*", Var("x"), Lit(2)))
    post_even = Divides(d=Lit(2), n=Result())

    rendered = render_lines([post_equal, post_even], names=nm, style=DividesStyle.OPERATIONAL)
    assert rendered == [
        "\\result == (x * 2)",
        "\\result % 2 == 0",
    ]

    annotations = [
        "requires 1 == 1",
        f"ensures {rendered[0]}",
        f"ensures {rendered[1]}",
        "assigns \\nothing",
    ]

    src = "def double(x: int) -> int:\n    return x * 2\n"
    annotated = annotate_source(src, "double", annotations)
    target = tmp_path / "double.annotated.py"
    target.write_text(annotated)

    v = _run_pipeline_or_skip(target, expected_count=2)

    assert v.exit_code == 0, (
        f"pycsl failed:\n"
        f"--- file ---\n{annotated}\n"
        f"--- stdout ---\n{v.stdout}\n"
        f"--- stderr ---\n{v.stderr}"
    )
    assert v.total >= 2, f"expected at least 2 obligations; got {v.total}:\n{v.stdout}"
    assert v.all_valid, v.summary()


def test_phase_a_round_trip_preserves_layout(tmp_path: Path):
    """The emitter must not perturb unrelated code or formatting.

    This is the property rocq2pycsl-plan.md §1 calls out: "preserve the
    user's Python formatting, comments, and unrelated code untouched".
    """
    src = (
        "# Euclidean algorithm.\n"
        "import math\n"
        "\n"
        "CONSTANT = 42  # not modified\n"
        "\n"
        "def helper(x: int) -> int:\n"
        "    return x + 1\n"
        "\n"
        "def target(x: int) -> int:\n"
        "    return x * 2\n"
    )
    annotated = annotate_source(
        src, "target", ["requires x >= 0", "ensures \\result >= 0", "assigns \\nothing"]
    )
    # Preconditions of the property:
    assert "# Euclidean algorithm." in annotated
    assert "import math" in annotated
    assert "CONSTANT = 42  # not modified" in annotated
    assert "def helper(x: int) -> int:\n    return x + 1" in annotated
    # And the new annotations sit flush against `target`:
    assert "#@ requires x >= 0\n#@ ensures \\result >= 0\n#@ assigns \\nothing\ndef target(" in annotated
