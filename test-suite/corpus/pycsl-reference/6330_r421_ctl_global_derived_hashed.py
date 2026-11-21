r"""Test 6330 -- route #421 (expected PASS): CONTROL: module globals / class-body names whose every binding a value-class row derives (arithmetic incl. unary minus, str concatenation, a tuple of primitives, a listed stdlib function, an annotated module function, an `if` / `else` union of ints, a class-body int) hashed as set elements under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
import os


def mk() -> int:
    return 3


K = 1 + 2
N = -1
SA = "a" + "b"
T = (1, "x")
P = os.path.join("a", "b")
G = mk()
if os.sep == "/":
    U = 1
else:
    U = 2


class C:
    K = 4


#@ no_exception \all
def f() -> int:
    hs = {K, N, G, U, C.K}
    ht = {SA, P}
    hu = {T}
    return len(hs) + len(ht) + len(hu)


if __name__ == "__main__":
    print(f())
