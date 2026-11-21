"""lvZ2 R614 helper (run #8): a Path alias built by a CALL (`TypeAliasType`) in a dependency, for
witness 10292 (red team rt70 m07)."""
from pathlib import Path
from typing import TypeAliasType

Fp = TypeAliasType("Fp", Path)


def mk(s: str) -> Fp:
    return Path(s)


def keep(x: str) -> str:
    return x
