r"""Test 9594 -- route #589 WITNESS (expected FAIL: REFUSED PYCSL-R589-RAISE-ARGUMENT-UNEVALUATED at HEAD, every model): no `no_exception` claim at all; an `except IndexError` handler makes the dropped `xs[9]` observable. CPython takes the IndexError arm and returns 2; the claim `\result == 1` is false.
"""
# pycsl-expected: FAIL
from typing import List


class E(Exception):
    pass


#@ ensures \result == 1
def f(xs: List[int]) -> int:
    try:
        raise E("a", xs[9])
    except IndexError:
        return 2
    except E:
        return 1
    return 0


if __name__ == "__main__":
    print(f([1]))
