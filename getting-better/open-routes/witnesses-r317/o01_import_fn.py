from typing import List
from rt16helper import poke

#@ ensures \result == 0
def f() -> int:
    ys = [0]
    poke(ys)
    return ys[0]

if __name__ == "__main__":
    assert f() == 0, f()
