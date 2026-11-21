r"""Test 6968 -- route #455 (expected FAIL): `from typing import overload`; `@overload def g` with no implementation, called `g(n)`. PROVED on main db6c57253 (red team 36 witness `c21_d000_overload_no_impl.py`); CPython raises NotImplementedError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R455-DECORATOR-SITE).
"""
# pycsl-expected: FAIL
from typing import overload


@overload
def g(a: int) -> int:
    return a


#@ no_exception \all
def f(n: int) -> int:
    return g(n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
