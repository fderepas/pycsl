"""pycsl_bridge — reconcile rocq2pycsl + lean2pycsl IR dumps.

Per pycsl-bridge-plan.md, the bridge solves two problems:

  - Linking — pair each Python qualname with the rocq + lean theorems
    that specify it (currently via the rocq2pycsl `spec_theorems` and
    the lean2pycsl `@[pycsl_spec "qualname"]` attribute; manifest is
    auto-generated from the IR dumps).
  - Reconciliation — canonicalize the IR coming from each side and
    confirm they agree. Disagreement surfaces as a structured diff
    instead of silently shipping mismatched contracts.

The package consumes the `--ir-dump` JSON from both Phase B tools and
produces:

  - An annotated Python file with dual attribution (or single-side
    attribution when only one formalism specs that function).
  - A `pycsl-bridge.manifest.toml` recording the pairings for CI
    drift detection.
  - A reconciliation report (status per qualname, structured diff
    on disagreement).
"""

__version__ = "0.1.0"
