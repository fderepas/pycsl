r"""Test 4863 -- gen #37 route #361 (expected FAIL): (new) `k: InitVar[int] = 7`: `D(1, 5).k` PROVED `\result == 5`; CPython reads the CLASS default 7. REFUSED (PYCSL-R361-DATACLASS-PSEUDO-FIELD, route #361).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, InitVar

@dataclass
class D:
    x: int
    k: InitVar[int] = 7

#@ ensures \result == 5
def f() -> int:
    d = D(1, 5)
    return d.k

if __name__ == "__main__":
    assert f() == 5, f()
