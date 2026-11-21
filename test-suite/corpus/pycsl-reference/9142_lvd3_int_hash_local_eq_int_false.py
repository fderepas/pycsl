r"""Test 9142 -- lvD3 (rt54 R54-F4 fi1536, expected FAIL): `name = "abc"; return name == x` with
`requires x == stable_hash("abc")` -- CPython compares a str with an int: False. C2 decided the int `=`
True. A comparison read is not an opaque position: C2 does not fire.
"""
# pycsl-expected: FAIL
from __future__ import annotations


#@ requires x == 1824800645
#@ ensures \result == True
#@ assigns \nothing
def f(x: int) -> bool:
    name = x
    name = "abc"
    return name == x


if __name__ == "__main__":
    r = f(1824800645)
    print("VIOLATION contract" if r is not True else "result", r)
