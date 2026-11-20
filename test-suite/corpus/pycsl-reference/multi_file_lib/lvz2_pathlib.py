"""lvZ2 helper (run #8): imported callees a modelled `Path(<str>)` is passed to, for witnesses
10280-10282 (red team rt70 m24 / m19 / m20)."""
from pathlib import Path
from typing import TypeAliasType

Fp = TypeAliasType("Fp", Path)


#@ ensures \result == p
#@ assigns \nothing
def ident(p: Path) -> Fp:
    return p


#@ ensures \result == x
#@ assigns \nothing
def keep(x: str) -> str:
    return x
