from pathlib import Path
from typing import TypeAliasType

Fp = TypeAliasType("Fp", Path)


#@ ensures True
#@ assigns \nothing
def mk(s: str) -> Fp:
    return Path(s)
