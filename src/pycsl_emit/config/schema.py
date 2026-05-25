"""Shared TOML schema for rocq2pycsl, lean2pycsl, and pycsl_bridge.

The schema is deliberately small — language-specific tools extend it
with their own sections (`[rocq]`, `[lean]`). What lives here is the
contract every tool must respect:

  [input]
    python  = "src/euclid.py"             # required
    output  = "src/euclid.annotated.py"   # optional; defaults to python.replace(".py", ".annotated.py")

  [pycsl]
    extra_flags = ["--memory-model", "hoare"]
    prover      = "Alt-Ergo,2.6.2,"
    timeout     = 120.0                    # wall-clock, in seconds

  [functions.<qualname>]
    python_name   = "gcd"                  # default: <qualname>
    arg_map       = { a = "a", b = "b" }   # proof-side → Python-side
    divides_style = "operational"           # operational | existential | guarded

Tools may add fields under their own sections (e.g. `[functions.gcd]` may
also carry `spec_theorems = [...]` for rocq2pycsl). This schema parses
only the shared parts and exposes everything else via `raw`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..translator import DividesStyle, NameMap


# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FunctionSpec:
    """Per-function configuration."""
    qualname: str
    python_name: str
    arg_map: NameMap
    divides_style: DividesStyle
    # Anything beyond the shared schema (e.g. `spec_theorems` for Rocq,
    # `extra_specs.include` for Lean). Consumed by the language tool.
    raw: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PycslSettings:
    """How to invoke the pycsl CLI."""
    extra_flags: tuple[str, ...] = ()
    prover: str | None = None
    timeout: float | None = 120.0

    def cli_args(self) -> list[str]:
        """Flatten to a list suitable for `run_pycsl(..., extra_args=...)`."""
        args: list[str] = list(self.extra_flags)
        if self.prover:
            args.extend(["-p", self.prover])
        return args


@dataclass(frozen=True)
class Config:
    """Top-level configuration."""
    python: str
    output: str
    functions: Mapping[str, FunctionSpec]
    pycsl: PycslSettings
    raw: Mapping[str, Any] = field(default_factory=dict)
