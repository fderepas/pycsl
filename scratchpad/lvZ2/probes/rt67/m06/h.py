from pathlib import Path
from typing import Tuple

#@ ensures \result[0] == p
#@ assigns \nothing
def pair(p: Path, n: int) -> Tuple[Path, int]:
    return (p, n)
