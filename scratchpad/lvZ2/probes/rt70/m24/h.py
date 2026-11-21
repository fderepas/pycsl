from pathlib import Path
from typing import TypeAliasType

Fp = TypeAliasType("Fp", Path)


#@ ensures \result == p
#@ assigns \nothing
def ident(p: Path) -> Fp:
    return p
