r"""Test 6776 -- route #443 (expected FAIL): an element of `List[T]` for a TypeVar `T` used as a method receiver. PROVED at base fa7cbb1aa under `#@ no_exception \all`; CPython AttributeError. Now REFUSED (PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE).
"""
# pycsl-expected: FAIL
from typing import List, TypeVar

T = TypeVar("T")


#@ no_exception \all
def f(xs: List[T]) -> int:
    if len(xs) == 0:
        return 0
    return len(xs[0].upper())


if __name__ == "__main__":
    try:
        print("result", f([1]))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
