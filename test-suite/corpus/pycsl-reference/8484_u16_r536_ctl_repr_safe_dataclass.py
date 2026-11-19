r"""Test 8484 -- route #536 (control, expected PASS): `str` / `repr` of a dataclass whose synthesized __repr__ formats only str / float fields (no int digit limit) stays a field initialiser; CPython f(P("a", 1.5)) returns 1
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    s: str
    x: float


class C:
    def __init__(self, p: P) -> None:
        self.k = str(p)
        self.r = repr(p)


#@ no_exception \all
#@ ensures \result == 1
def f(p: P) -> int:
    c = C(p)
    return 1


if __name__ == "__main__":
    print(f(P("a", 1.5)))
