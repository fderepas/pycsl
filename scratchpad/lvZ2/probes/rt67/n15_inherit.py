from __future__ import annotations
from pathlib import Path


class Base:
    #@ assigns \nothing
    def __init__(self, s: str) -> None:
        self.s = s

    #@ assigns \nothing
    def mk(self) -> Path:
        return Path(self.s)


class Sub(Base):
    pass


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    o = Sub(s)
    v = o.mk()
    return v == str(v)


if __name__ == "__main__":
    print("result", f("a"))
