r"""Test 8816 -- route #560 (control, expected PASS): IntEnum members bound to a local and computed / compared as ints (`x - x`, `k == IE.B`), never searched or iterated themselves; CPython 0 1
"""
# pycsl-expected: PASS
import enum


class IE(enum.IntEnum):
    A = 1
    B = 2


#@ no_exception \all
#@ ensures \result == 0
def f(k: int) -> int:
    x = IE.A
    return x - x


#@ no_exception \all
def g(k: int) -> int:
    if k == IE.B:
        return 1
    return 0


if __name__ == "__main__":
    print(f(0), g(2))
