r"""Test 7992 -- route #504 (control, expected PASS): `k = K(n); return k.a is k.a` -- two reads of ONE stored int field are one object; CPython True
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class K:
    def __init__(self, n: int) -> None:
        self.a = n + 1000
        self.b = n + 1000


#@ ensures \result == True
def f(n: int) -> bool:
    k = K(n)
    return k.a is k.a


if __name__ == "__main__":
    assert f(5) == True
