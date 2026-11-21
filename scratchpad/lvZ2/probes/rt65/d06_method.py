from __future__ import annotations
from pathlib import Path


class K:
    #@ ensures \result == True
    #@ assigns \nothing
    def m(self, s: str) -> bool:
        p = Path(s)
        return p == str(p)


if __name__ == "__main__":
    print("result", K().m("a"))
