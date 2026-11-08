r"""Test 4862 -- gen #37 route #361 (expected FAIL): witness r29: `D(1, 5).k` PROVED `\result == 5` (CPython AttributeError). REFUSED (PYCSL-R361-DATACLASS-PSEUDO-FIELD, route #361).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, InitVar

@dataclass
class D:
    x: int
    k: InitVar[int]

#@ ensures \result == 5
def f() -> int:
    d = D(1, 5)
    return d.k

if __name__ == "__main__":
    print(f())
