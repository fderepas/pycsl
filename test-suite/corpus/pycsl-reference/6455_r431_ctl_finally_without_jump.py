r"""Test 6455 -- route #431 (expected PASS): CONTROL: a handler-less `try ... finally:` whose `finally` block does not jump, followed by a `return` after the `try` statement (the advice of PYCSL-R431). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import List


#@ requires len(out) == 1
#@ ensures out[0] == 1
#@ assigns out[0]
def f(out: List[int]) -> None:
    out[0] = 2
    try:
        out[0] = 1
    finally:
        x = 0
    return


if __name__ == "__main__":
    o = [0]
    f(o)
    print(o)
