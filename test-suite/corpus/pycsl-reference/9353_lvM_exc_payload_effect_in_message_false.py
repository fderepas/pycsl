r"""Test 9353 -- cap-exception-payload-model (expected FAIL: the claim is FALSE of the program): the payload
is the raise's FIRST CONSTRUCTOR ARGUMENT, lowered at its Python position, so a call that builds the message is
evaluated exactly once before the raise. `bump(xs)` writes `xs[0] = 1` and the claim `\result == 0` is
false (CPython returns 1).
"""
# pycsl-expected: FAIL
from typing import List


class Oops(Exception):
    pass


#@ requires len(xs) == 1
#@ ensures xs[0] == 1
#@ assigns xs[0]
def bump(xs: List[int]) -> str:
    xs[0] = 1
    return "bumped"


#@ requires True
#@ ensures \result == 0
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
    print("VIOLATION contract" if r != 0 else "ok", r)
