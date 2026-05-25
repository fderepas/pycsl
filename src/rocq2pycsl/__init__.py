"""rocq2pycsl — extract PyCSL contracts from a Rocq .v file.

The plan (see /rocq2pycsl-plan.md): treat Rocq theorems as a trusted
oracle for *what the contracts should say*, then run pycsl on the
annotated Python to discharge them independently.

Two extractor backends share a small Gallina surface AST:

  - extractor.lark_backend    (default, no opam dependencies)
  - extractor.serapi_backend  (--backend=serapi; sertop subprocess)

Both produce the same `gallina.Theorem` / `gallina.FunctionDef` nodes,
which `translator.gallina` walks into the shared pycsl_emit IR.
"""

__version__ = "0.1.0"
