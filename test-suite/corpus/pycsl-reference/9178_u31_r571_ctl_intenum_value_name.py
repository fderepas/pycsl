r"""Test 9178 -- route #571 (control, expected PASS): IntEnum members used correctly -- `.value` in arithmetic, compared with an int, as an element of a searched list display, bound to a local; `.name` compared with `==` only; CPython 2 1 1 1 4
"""
# pycsl-expected: PASS
import enum


class IE(enum.IntEnum):
    A = 1
    B = 2


#@ no_exception \all
def f1(k: int) -> int:
    return IE.A.value + 1


#@ no_exception \all
def f2(k: int) -> int:
    return 1 if k == IE.B.value else 0


#@ no_exception \all
def f3(k: int) -> int:
    return 1 if IE.A.name == "A" else 0


#@ no_exception \all
def f4(k: int) -> int:
    return 1 if k in [IE.A.value, 3] else 0


#@ no_exception \all
def f5(k: int) -> int:
    v = IE.B.value
    return v * 2


if __name__ == "__main__":
    print(f1(1), f2(2), f3(1), f4(1), f5(1))
