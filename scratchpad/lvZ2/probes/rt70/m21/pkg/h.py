from pathlib import Path

#@ ensures \result == p
#@ assigns \nothing
def ident(p: Path) -> Path:
    return p
