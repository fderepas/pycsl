"""lean2pycsl — extract PyCSL contracts from a Lean 4 .lean file.

The plan (see /lean2pycsl-plan.md): treat Lean theorems as a trusted
oracle for *what the contracts should say*, then run pycsl on the
annotated Python to discharge them independently.

Two extractor backends share a small Lean surface AST:

  - extractor.lark_backend        (default, no Lean toolchain required)
  - extractor.lean_script_backend (--backend=lean-script; lake env lean)

Both produce the same `lean_ast.Theorem` / `lean_ast.LeanDef` nodes,
which `translator.lean` walks into the shared pycsl_emit IR.
"""

__version__ = "0.1.0"
