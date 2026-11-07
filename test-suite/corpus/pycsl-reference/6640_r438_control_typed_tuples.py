r"""Test 6640 -- route #438 (expected PASS): CONTROL: a PARAMETERISED tuple (`Tuple[int, str]`, a field `Tuple[str, int]`, a tuple display of typed values) hashed under `no_exception \all`, and a bare `t: tuple` hashed in an UN-claimed function (its TypeError is ambient there), are not refused. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Tuple

class R:
    def __init__(self, t: Tuple[str, int]) -> None:
        self.t: Tuple[str, int] = t


#@ no_exception \all
#@ ensures \result == n + 1
def f(a: Tuple[int, str], r: R, n: int) -> int:
    s = {a, (1, "x")}
    u = {r.t}
    return n + 1


#@ ensures \result == n + 1
def g(t: tuple, n: int) -> int:
    s = {t}
    return n + 1


if __name__ == "__main__":
    try:
        r = f((1, "a"), R(("x", 1)), 1) + g((1,), 1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
