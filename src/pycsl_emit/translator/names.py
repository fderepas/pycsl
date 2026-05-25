"""Identifier remapping from proof side to Python side.

The proof developer may have used `a, b` while the Python implementation
uses `x, y`. The TOML config supplies an `arg_map` per function; this
module wraps it as a small object the translator passes around.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class NameMap:
    """Identity map by default; override specific names via `mapping`."""
    mapping: Mapping[str, str] = field(default_factory=dict)

    def apply(self, name: str) -> str:
        return self.mapping.get(name, name)

    @classmethod
    def identity(cls) -> "NameMap":
        return cls(mapping={})
