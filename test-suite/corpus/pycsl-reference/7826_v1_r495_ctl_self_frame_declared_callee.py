r"""Test 7826 -- route #495 (control, expected PASS; the advice followed): witness 7815 with the `assigns \nothing` clause deleted (`__len__` declares only `#@ assigns self.v`), the `\trusted` k declares `#@ assigns o.v`, and the caller no longer claims `o.v` unchanged; CPython returns 0
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self) -> None:
        self.v = 0

    #@ assigns self.v
    def __len__(self) -> int:
        self.v = 7
        return 1


#@ \trusted
#@ assigns o.v
def k(o: C) -> int:
    return len(o)


#@ ensures \result == 0
def f(n: int) -> int:
    o = C()
    k(o)
    return 0


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
