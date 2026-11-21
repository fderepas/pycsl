from __future__ import annotations
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path


class C:
    #@ ensures \result == True
    #@ assigns \nothing
    def m(self, p: Fp) -> bool:
        return p == str(p)


if __name__ == "__main__":
    print("result", C().m(Path("a")))
