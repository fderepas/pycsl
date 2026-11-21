r"""Test 9605 -- route #589 WITNESS (expected FAIL: REFUSED PYCSL-R589-RAISE-ARGUMENT-UNEVALUATED at HEAD, every model): the dropped argument lives in an IMPORTED callee (`multi_file_lib/r589_raising.py`: `raise E589("a", xs[9])`), whose exported contract `raises E589` is all this file's `except IndexError` arm sees, so the arm was dead in the proof. CPython takes it and returns 2; the claim `\result != 2` is false.
"""
# pycsl-expected: FAIL
from typing import List
from multi_file_lib.r589_raising import g589, E589


#@ ensures \result != 2
def f(xs: List[int]) -> int:
    try:
        g589(xs)
    except IndexError:
        return 2
    except E589:
        return 1
    return 0


if __name__ == "__main__":
    print(f([1]))
