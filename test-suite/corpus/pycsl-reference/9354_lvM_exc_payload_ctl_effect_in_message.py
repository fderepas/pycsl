r"""Test 9354 -- cap-exception-payload-model CONTROL of 9353 (expected PASS): the honest claim `\result == 1`
(CPython 1) proves: the call that builds the raised message is evaluated once, at its Python position.
"""
# pycsl-expected: PASS
from typing import List


class Oops(Exception):
    pass


#@ requires len(xs) == 1
#@ ensures xs[0] == 1
#@ assigns xs[0]
def bump(xs: List[int]) -> str:
    xs[0] = 1
    return "bumped"


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    xs: List[int] = [0]
    try:
        raise Oops(bump(xs))
    except Oops:
        pass
    return xs[0]


if __name__ == "__main__":
    r = probe()
    print("VIOLATION contract" if r != 1 else "ok", r)
