"""SerAPI extractor backend (v2 stub).

The plan §10.3 flags SerAPI as version-fragile and treats it as the
highest-risk external dependency. The Lark backend is the v1 default
for that reason; this file holds the API surface that a future SerAPI
implementation will fill in.

Status: stub. Invoking this backend raises NotImplementedError with
install instructions. Once `coq-serapi.8.20.0+0.20.0` is wired in, the
implementation should:

  1. Spawn `sertop --printer=sertop` as a long-lived subprocess.
  2. Add the file's vernac commands one at a time via
     `(Add () "<command>")`, parsing the returned `(Answer …)` sexps.
  3. For each tagged theorem / definition, issue
     `(Query () (Type <name>))` and parse the elaborated Constr sexp.
  4. Map elaborated Constrs onto the same `GallinaModule` shape this
     module exposes — so downstream code is backend-agnostic.

The `sertop_available()` helper is exposed so the CLI can detect
whether `--backend=serapi` is realistically usable in the current
environment and fall back / error out cleanly.
"""

from __future__ import annotations

import shutil

from .gallina import GallinaModule


_INSTALL_HINT = (
    "SerAPI backend is not yet implemented (v1 ships with the Lark backend).\n"
    "When implemented, this backend requires `sertop` on PATH.\n"
    "  opam install coq-serapi.8.20.0+0.20.0   # match your Coq version\n"
    "For v1, omit --backend or pass --backend=lark."
)


def sertop_available() -> bool:
    """Return True iff `sertop` is on PATH."""
    return shutil.which("sertop") is not None


def parse_module(text: str, *, source_path: str = "") -> GallinaModule:
    """Stub. Raises NotImplementedError with install instructions.

    Kept as a callable so the api.extract() dispatcher can route to it
    without import-time failure when the v1 Lark default is in use.
    """
    raise NotImplementedError(_INSTALL_HINT)
