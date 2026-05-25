"""Lean-script extractor backend (v2 stub).

When implemented, this backend will:

  1. Ship a `lean_side/PycslExport.lean` library defining the
     `@[pycsl_spec ident]` attribute and a `#pycsl_export` command.
  2. Generate a temp `Probe.lean` that imports both the user's file
     and the library, then runs `#pycsl_export` to dump tagged decls
     as JSON.
  3. Invoke `lake env lean --run Probe.lean` from the user's lake
     project root.
  4. Parse the JSON output into `LeanModule` nodes — same shape as
     the Lark backend so the rest of the pipeline doesn't care.

The Lean toolchain is already installed on this dev machine (lean
4.29.1, lake 5.0.0). The plan §10 notes this should ship both as a
Lake dep and as a Python package. The Python side is in place; the
Lean side is deferred to v2.

Status: stub. Invoking this backend raises NotImplementedError with
install instructions. The `lake_available()` helper lets the CLI
detect availability for future runtime decisions.
"""

from __future__ import annotations

import shutil

from .lean_ast import LeanModule


_INSTALL_HINT = (
    "Lean-script backend is not yet implemented "
    "(v1 ships with the Lark backend).\n"
    "When implemented, this backend requires the Lean toolchain "
    "(`lake` on PATH).\n"
    "  curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh\n"
    "For v1, omit --backend or pass --backend=lark."
)


def lake_available() -> bool:
    """Return True iff `lake` is on PATH."""
    return shutil.which("lake") is not None


def parse_module(text: str, *, source_path: str = "") -> LeanModule:
    """Stub. Raises NotImplementedError with install instructions."""
    raise NotImplementedError(_INSTALL_HINT)
