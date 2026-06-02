"""End-to-end golden test for pycsl-bridge.

The test reuses the *existing* Phase B `double` fixtures from
rocq2pycsl and lean2pycsl. The bridge:

  1. Runs both converters in --ir-dump mode.
  2. Canonicalizes and confirms they agree (RECONCILED).
  3. Emits annotated Python with dual `# proof rocq:` / `# proof lean:`
     traceability comments plus the standard `#@` contract block.
  4. Writes a manifest recording the pairing.
  5. Re-runs pycsl on the emitted file and confirms all obligations
     discharge.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from pycsl_bridge.cli import run as bridge_run
from pycsl_bridge.linker.manifest import read_manifest
from pycsl_bridge.reconciler import Status


_ROCQ_GOLDEN = Path(__file__).resolve().parents[2] / "rocq2pycsl" / "tests" / "golden" / "double"
_LEAN_GOLDEN = Path(__file__).resolve().parents[2] / "lean2pycsl" / "tests" / "golden" / "double"
_BRIDGE_GOLDEN = Path(__file__).resolve().parent / "golden" / "double"

_ROCQ_BOOL_XOR = Path(__file__).resolve().parents[2] / "rocq2pycsl" / "tests" / "golden" / "bool_xor"
_LEAN_BOOL_XOR = Path(__file__).resolve().parents[2] / "lean2pycsl" / "tests" / "golden" / "bool_xor"
_BRIDGE_BOOL_XOR = Path(__file__).resolve().parent / "golden" / "bool_xor"


def _stage(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Copy both Phase B fixtures + the shared impl.py into tmp_path
    and return (rocq_config, lean_config, python_src) paths."""
    rocq_dir = tmp_path / "rocq"
    lean_dir = tmp_path / "lean"
    rocq_dir.mkdir()
    lean_dir.mkdir()
    for name in ("spec.v", "config.toml"):
        (rocq_dir / name).write_text((_ROCQ_GOLDEN / name).read_text())
    for name in ("spec.lean", "config.toml"):
        (lean_dir / name).write_text((_LEAN_GOLDEN / name).read_text())
    # impl.py lives at the bridge level — both fixtures share it.
    impl = tmp_path / "impl.py"
    impl.write_text((_ROCQ_GOLDEN / "impl.py").read_text())
    # Both configs reference `impl.py` locally; copy it inside both dirs.
    (rocq_dir / "impl.py").write_text(impl.read_text())
    (lean_dir / "impl.py").write_text(impl.read_text())
    return rocq_dir / "config.toml", lean_dir / "config.toml", impl


def _stage_bool_xor(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Like `_stage` but for the bool_xor pilot fixture from tuesday-01."""
    rocq_dir = tmp_path / "rocq"
    lean_dir = tmp_path / "lean"
    rocq_dir.mkdir()
    lean_dir.mkdir()
    for name in ("spec.v", "config.toml"):
        (rocq_dir / name).write_text((_ROCQ_BOOL_XOR / name).read_text())
    for name in ("spec.lean", "config.toml"):
        (lean_dir / name).write_text((_LEAN_BOOL_XOR / name).read_text())
    impl = tmp_path / "impl.py"
    impl.write_text((_ROCQ_BOOL_XOR / "impl.py").read_text())
    (rocq_dir / "impl.py").write_text(impl.read_text())
    (lean_dir / "impl.py").write_text(impl.read_text())
    return rocq_dir / "config.toml", lean_dir / "config.toml", impl


def test_bridge_reconciles_bank_account_fixture(tmp_path: Path):
    """Phase 6 — class fixture through the bridge with arg_map applied.

    Two methods (deposit/withdraw) each get their own per-method
    contract block, with the receiver `balance` parameter rewritten
    to `self._balance` via arg_map. The class invariant in the source
    is preserved through annotation."""
    rocq_dir = tmp_path / "rocq"
    lean_dir = tmp_path / "lean"
    rocq_dir.mkdir()
    lean_dir.mkdir()
    _ROCQ = Path(__file__).resolve().parents[2] / "rocq2pycsl" / "tests" / "golden" / "bank_account"
    _LEAN = Path(__file__).resolve().parents[2] / "lean2pycsl" / "tests" / "golden" / "bank_account"
    _BRIDGE = Path(__file__).resolve().parent / "golden" / "bank_account"
    for name in ("spec.v", "config.toml"):
        (rocq_dir / name).write_text((_ROCQ / name).read_text())
    for name in ("spec.lean", "config.toml"):
        (lean_dir / name).write_text((_LEAN / name).read_text())
    impl = tmp_path / "impl.py"
    impl.write_text((_ROCQ / "impl.py").read_text())
    (rocq_dir / "impl.py").write_text(impl.read_text())
    (lean_dir / "impl.py").write_text(impl.read_text())

    outcome = bridge_run(
        rocq_config=rocq_dir / "config.toml",
        lean_config=lean_dir / "config.toml",
        python_src=impl,
        output=tmp_path / "bank_account.annotated.py",
        manifest=tmp_path / "manifest.toml",
        on_disagreement="halt",
        no_check=True,
    )

    assert "BankAccount.deposit" in outcome.reconciliation.results
    assert "BankAccount.withdraw" in outcome.reconciliation.results
    assert outcome.disagreements == []
    expected = (_BRIDGE / "expected.py").read_text()
    assert outcome.annotated_source == expected


@pytest.mark.parametrize(
    "fixture_name",
    ["array_fill_zero", "list_length_after_append", "set_union_eq"],
)
def test_bridge_reconciles_tuesday01_phase5_fixture(tmp_path: Path, fixture_name: str):
    """Parametrized bridge reconciliation for the remaining tuesday-01
    Phase 5 fixtures (array_fill_zero, ghost_list, ghost_set). Golden
    cross-prover output capture only — PyCSL discharge for these is
    out of scope (needs ghost variable / frame-condition support)."""
    rocq_dir = tmp_path / "rocq"
    lean_dir = tmp_path / "lean"
    rocq_dir.mkdir()
    lean_dir.mkdir()
    _ROCQ = Path(__file__).resolve().parents[2] / "rocq2pycsl" / "tests" / "golden" / fixture_name
    _LEAN = Path(__file__).resolve().parents[2] / "lean2pycsl" / "tests" / "golden" / fixture_name
    _BRIDGE = Path(__file__).resolve().parent / "golden" / fixture_name
    for name in ("spec.v", "config.toml"):
        (rocq_dir / name).write_text((_ROCQ / name).read_text())
    for name in ("spec.lean", "config.toml"):
        (lean_dir / name).write_text((_LEAN / name).read_text())
    impl = tmp_path / "impl.py"
    impl.write_text((_ROCQ / "impl.py").read_text())
    (rocq_dir / "impl.py").write_text(impl.read_text())
    (lean_dir / "impl.py").write_text(impl.read_text())

    outcome = bridge_run(
        rocq_config=rocq_dir / "config.toml",
        lean_config=lean_dir / "config.toml",
        python_src=impl,
        output=tmp_path / f"{fixture_name}.annotated.py",
        manifest=tmp_path / "manifest.toml",
        on_disagreement="halt",
        no_check=True,
    )

    assert fixture_name in outcome.reconciliation.results
    assert outcome.reconciliation.results[fixture_name].status is Status.RECONCILED
    expected = (_BRIDGE / "expected.py").read_text()
    assert outcome.annotated_source == expected


def test_bridge_reconciles_dict_insert_lookup_fixture(tmp_path: Path):
    """Dict-as-function fixture through the bridge."""
    rocq_dir = tmp_path / "rocq"
    lean_dir = tmp_path / "lean"
    rocq_dir.mkdir()
    lean_dir.mkdir()
    _ROCQ_DI = Path(__file__).resolve().parents[2] / "rocq2pycsl" / "tests" / "golden" / "dict_insert_lookup"
    _LEAN_DI = Path(__file__).resolve().parents[2] / "lean2pycsl" / "tests" / "golden" / "dict_insert_lookup"
    _BRIDGE_DI = Path(__file__).resolve().parent / "golden" / "dict_insert_lookup"
    for name in ("spec.v", "config.toml"):
        (rocq_dir / name).write_text((_ROCQ_DI / name).read_text())
    for name in ("spec.lean", "config.toml"):
        (lean_dir / name).write_text((_LEAN_DI / name).read_text())
    impl = tmp_path / "impl.py"
    impl.write_text((_ROCQ_DI / "impl.py").read_text())
    (rocq_dir / "impl.py").write_text(impl.read_text())
    (lean_dir / "impl.py").write_text(impl.read_text())

    outcome = bridge_run(
        rocq_config=rocq_dir / "config.toml",
        lean_config=lean_dir / "config.toml",
        python_src=impl,
        output=tmp_path / "dict_insert_lookup.annotated.py",
        manifest=tmp_path / "manifest.toml",
        on_disagreement="halt",
        no_check=True,
    )

    assert "dict_insert_lookup" in outcome.reconciliation.results
    assert outcome.reconciliation.results["dict_insert_lookup"].status is Status.RECONCILED
    expected = (_BRIDGE_DI / "expected.py").read_text()
    assert outcome.annotated_source == expected


def test_bridge_reconciles_array_sum_nonneg_fixture(tmp_path: Path):
    """List-parameter fixture with auto-emitted `requires n >= 0`."""
    rocq_dir = tmp_path / "rocq"
    lean_dir = tmp_path / "lean"
    rocq_dir.mkdir()
    lean_dir.mkdir()
    _ROCQ_AS = Path(__file__).resolve().parents[2] / "rocq2pycsl" / "tests" / "golden" / "array_sum_nonneg"
    _LEAN_AS = Path(__file__).resolve().parents[2] / "lean2pycsl" / "tests" / "golden" / "array_sum_nonneg"
    _BRIDGE_AS = Path(__file__).resolve().parent / "golden" / "array_sum_nonneg"
    for name in ("spec.v", "config.toml"):
        (rocq_dir / name).write_text((_ROCQ_AS / name).read_text())
    for name in ("spec.lean", "config.toml"):
        (lean_dir / name).write_text((_LEAN_AS / name).read_text())
    impl = tmp_path / "impl.py"
    impl.write_text((_ROCQ_AS / "impl.py").read_text())
    (rocq_dir / "impl.py").write_text(impl.read_text())
    (lean_dir / "impl.py").write_text(impl.read_text())

    outcome = bridge_run(
        rocq_config=rocq_dir / "config.toml",
        lean_config=lean_dir / "config.toml",
        python_src=impl,
        output=tmp_path / "array_sum_nonneg.annotated.py",
        manifest=tmp_path / "manifest.toml",
        on_disagreement="halt",
        no_check=True,
    )

    assert "array_sum_nonneg" in outcome.reconciliation.results
    assert outcome.reconciliation.results["array_sum_nonneg"].status is Status.RECONCILED
    expected = (_BRIDGE_AS / "expected.py").read_text()
    assert outcome.annotated_source == expected


def test_bridge_reconciles_concat_length_fixture(tmp_path: Path):
    """Strings: Coq's `String.length` and Lean's `s.length` dot syntax
    both lower to `StrLength`. Cross-prover convergence test."""
    rocq_dir = tmp_path / "rocq"
    lean_dir = tmp_path / "lean"
    rocq_dir.mkdir()
    lean_dir.mkdir()
    _ROCQ_CL = Path(__file__).resolve().parents[2] / "rocq2pycsl" / "tests" / "golden" / "concat_length"
    _LEAN_CL = Path(__file__).resolve().parents[2] / "lean2pycsl" / "tests" / "golden" / "concat_length"
    _BRIDGE_CL = Path(__file__).resolve().parent / "golden" / "concat_length"
    for name in ("spec.v", "config.toml"):
        (rocq_dir / name).write_text((_ROCQ_CL / name).read_text())
    for name in ("spec.lean", "config.toml"):
        (lean_dir / name).write_text((_LEAN_CL / name).read_text())
    impl = tmp_path / "impl.py"
    impl.write_text((_ROCQ_CL / "impl.py").read_text())
    (rocq_dir / "impl.py").write_text(impl.read_text())
    (lean_dir / "impl.py").write_text(impl.read_text())

    outcome = bridge_run(
        rocq_config=rocq_dir / "config.toml",
        lean_config=lean_dir / "config.toml",
        python_src=impl,
        output=tmp_path / "concat_length.annotated.py",
        manifest=tmp_path / "manifest.toml",
        on_disagreement="halt",
        no_check=True,
    )

    assert "concat_length" in outcome.reconciliation.results
    assert outcome.reconciliation.results["concat_length"].status is Status.RECONCILED
    expected = (_BRIDGE_CL / "expected.py").read_text()
    assert outcome.annotated_source == expected


def test_bridge_reconciles_divmod_pair_fixture(tmp_path: Path):
    """Tuple-returning fixture through the bridge. Both prover sides
    use different surface syntax (Coq's `fst`/`snd` vs Lean's dot
    syntax) but converge on the same Proj-based IR."""
    rocq_dir = tmp_path / "rocq"
    lean_dir = tmp_path / "lean"
    rocq_dir.mkdir()
    lean_dir.mkdir()
    _ROCQ_DM = Path(__file__).resolve().parents[2] / "rocq2pycsl" / "tests" / "golden" / "divmod_pair"
    _LEAN_DM = Path(__file__).resolve().parents[2] / "lean2pycsl" / "tests" / "golden" / "divmod_pair"
    _BRIDGE_DM = Path(__file__).resolve().parent / "golden" / "divmod_pair"
    for name in ("spec.v", "config.toml"):
        (rocq_dir / name).write_text((_ROCQ_DM / name).read_text())
    for name in ("spec.lean", "config.toml"):
        (lean_dir / name).write_text((_LEAN_DM / name).read_text())
    impl = tmp_path / "impl.py"
    impl.write_text((_ROCQ_DM / "impl.py").read_text())
    (rocq_dir / "impl.py").write_text(impl.read_text())
    (lean_dir / "impl.py").write_text(impl.read_text())

    outcome = bridge_run(
        rocq_config=rocq_dir / "config.toml",
        lean_config=lean_dir / "config.toml",
        python_src=impl,
        output=tmp_path / "divmod_pair.annotated.py",
        manifest=tmp_path / "manifest.toml",
        on_disagreement="halt",
        no_check=True,
    )

    assert "divmod_pair" in outcome.reconciliation.results
    assert outcome.reconciliation.results["divmod_pair"].status is Status.RECONCILED
    assert outcome.disagreements == []

    expected = (_BRIDGE_DM / "expected.py").read_text()
    assert outcome.annotated_source == expected


def test_bridge_reconciles_bool_xor_fixture(tmp_path: Path):
    """Phase 5 pilot: cross-prover reconciliation for boolean XOR.

    Demonstrates that the new IR/canonicalizer/translator support added
    in Phases 1–4 of tuesday-01 closes the loop end-to-end for the
    first new data type (booleans, via the 0/1 encoding)."""
    rocq_cfg, lean_cfg, impl_py = _stage_bool_xor(tmp_path)

    outcome = bridge_run(
        rocq_config=rocq_cfg,
        lean_config=lean_cfg,
        python_src=impl_py,
        output=tmp_path / "bool_xor.annotated.py",
        manifest=tmp_path / "pycsl-bridge.manifest.toml",
        on_disagreement="halt",
        no_check=True,
        verbose=False,
    )

    assert "bool_xor" in outcome.reconciliation.results
    assert outcome.reconciliation.results["bool_xor"].status is Status.RECONCILED
    assert outcome.disagreements == []

    expected = (_BRIDGE_BOOL_XOR / "expected.py").read_text()
    assert outcome.annotated_source == expected


def test_bridge_reconciles_double_fixture(tmp_path: Path):
    rocq_cfg, lean_cfg, impl_py = _stage(tmp_path)

    outcome = bridge_run(
        rocq_config=rocq_cfg,
        lean_config=lean_cfg,
        python_src=impl_py,
        output=tmp_path / "double.annotated.py",
        manifest=tmp_path / "pycsl-bridge.manifest.toml",
        on_disagreement="halt",
        no_check=True,
        verbose=False,
    )

    # Reconciliation status — the headline assertion of Phase C.
    assert "double" in outcome.reconciliation.results
    assert outcome.reconciliation.results["double"].status is Status.RECONCILED
    assert outcome.disagreements == []


def test_bridge_emits_dual_attribution(tmp_path: Path):
    rocq_cfg, lean_cfg, impl_py = _stage(tmp_path)

    outcome = bridge_run(
        rocq_config=rocq_cfg,
        lean_config=lean_cfg,
        python_src=impl_py,
        output=tmp_path / "double.annotated.py",
        manifest=tmp_path / "pycsl-bridge.manifest.toml",
        no_check=True,
    )

    expected = (_BRIDGE_GOLDEN / "expected.py").read_text()
    actual = outcome.annotated_source
    assert actual == expected, (
        "bridge output drift:\n"
        f"--- expected ---\n{expected}\n"
        f"--- actual ---\n{actual}\n"
    )


def test_bridge_writes_manifest_with_correct_pairing(tmp_path: Path):
    rocq_cfg, lean_cfg, impl_py = _stage(tmp_path)
    manifest_path = tmp_path / "pycsl-bridge.manifest.toml"

    bridge_run(
        rocq_config=rocq_cfg,
        lean_config=lean_cfg,
        python_src=impl_py,
        output=tmp_path / "double.annotated.py",
        manifest=manifest_path,
        no_check=True,
    )

    m = read_manifest(manifest_path)
    assert len(m.entries) == 1
    e = m.entries[0]
    assert e.python == "double"
    assert e.rocq == ("double_value", "double_is_even")
    assert e.lean == ("double_value", "double_is_even")
    assert e.status == "reconciled"


def test_bridge_full_round_trip_through_pycsl(tmp_path: Path):
    """End-to-end: bridge → annotated.py → pycsl → all obligations Valid."""
    rocq_cfg, lean_cfg, impl_py = _stage(tmp_path)
    annotated = tmp_path / "double.annotated.py"

    outcome = bridge_run(
        rocq_config=rocq_cfg,
        lean_config=lean_cfg,
        python_src=impl_py,
        output=annotated,
        manifest=tmp_path / "manifest.toml",
        on_disagreement="halt",
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


def test_bridge_halts_on_disagreement(tmp_path: Path):
    """Tamper with one side to introduce a disagreement; halt mode
    must not emit annotated Python."""
    rocq_cfg, lean_cfg, impl_py = _stage(tmp_path)

    # Strip `double_is_even` from the rocq config so the rocq side
    # only emits one ensures while lean emits two.
    cfg_text = rocq_cfg.read_text()
    cfg_text = cfg_text.replace(
        'spec_theorems    = ["double_value", "double_is_even"]',
        'spec_theorems    = ["double_value"]',
    )
    rocq_cfg.write_text(cfg_text)
    annotated = tmp_path / "double.annotated.py"

    outcome = bridge_run(
        rocq_config=rocq_cfg,
        lean_config=lean_cfg,
        python_src=impl_py,
        output=annotated,
        manifest=tmp_path / "manifest.toml",
        on_disagreement="halt",
        no_check=True,
    )

    assert len(outcome.disagreements) == 1
    assert outcome.disagreements[0].status is Status.DISAGREEMENT
    # halt mode should not produce annotated Python.
    assert outcome.annotated_source is None
    assert not annotated.exists()
    # But the manifest IS written so CI can see the divergence state.
    assert outcome.manifest_path is not None and outcome.manifest_path.exists()


def test_bridge_force_emits_despite_disagreement(tmp_path: Path):
    rocq_cfg, lean_cfg, impl_py = _stage(tmp_path)
    cfg_text = rocq_cfg.read_text().replace(
        'spec_theorems    = ["double_value", "double_is_even"]',
        'spec_theorems    = ["double_value"]',
    )
    rocq_cfg.write_text(cfg_text)

    outcome = bridge_run(
        rocq_config=rocq_cfg,
        lean_config=lean_cfg,
        python_src=impl_py,
        output=tmp_path / "double.annotated.py",
        manifest=tmp_path / "manifest.toml",
        on_disagreement="force",
        no_check=True,
    )

    # force mode still records the disagreement but emits anyway.
    assert outcome.disagreements
    assert outcome.annotated_source is not None
    # The rocq side is chosen by default — only `double_value` survives.
    assert outcome.annotated_source.count("ensures") == 1


def test_bridge_check_mode_passes_when_manifest_is_fresh(tmp_path: Path):
    rocq_cfg, lean_cfg, impl_py = _stage(tmp_path)
    manifest_path = tmp_path / "manifest.toml"

    bridge_run(
        rocq_config=rocq_cfg,
        lean_config=lean_cfg,
        python_src=impl_py,
        output=tmp_path / "double.annotated.py",
        manifest=manifest_path,
        no_check=True,
    )
    # Now --check: the on-disk manifest matches the regenerated one.
    bridge_run(
        rocq_config=rocq_cfg,
        lean_config=lean_cfg,
        manifest=manifest_path,
        check_manifest_only=True,
        no_check=True,
    )  # does not raise


def test_bridge_check_mode_fails_on_drift(tmp_path: Path):
    rocq_cfg, lean_cfg, impl_py = _stage(tmp_path)
    manifest_path = tmp_path / "manifest.toml"

    bridge_run(
        rocq_config=rocq_cfg,
        lean_config=lean_cfg,
        python_src=impl_py,
        output=tmp_path / "double.annotated.py",
        manifest=manifest_path,
        no_check=True,
    )

    # Edit the rocq config so the next run would produce a different
    # manifest, then `--check` against the old one.
    cfg_text = rocq_cfg.read_text().replace(
        'spec_theorems    = ["double_value", "double_is_even"]',
        'spec_theorems    = ["double_value"]',
    )
    rocq_cfg.write_text(cfg_text)
    with pytest.raises(ValueError, match="manifest out of date"):
        bridge_run(
            rocq_config=rocq_cfg,
            lean_config=lean_cfg,
            manifest=manifest_path,
            check_manifest_only=True,
            no_check=True,
        )
