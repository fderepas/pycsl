r"""Test 10178 -- route #612 CONTROL (expected PASS): the repair the refusal advises. The callable is a verified function of the program called BY NAME, so its contract (not an assumed pure arrow) decides `twice(3) == 8`, and two calls are equal because the verified body is deterministic. A `Callable` parameter declared alongside stays admissible.
"""
# pycsl-expected: PASS
from typing import Callable


#@ ensures \result == x + 1
#@ assigns \nothing
def inc(x: int) -> int:
    return x + 1


#@ ensures \result == x + 2
#@ assigns \nothing
def twice(cb: Callable[[int], int], x: int) -> int:
    return inc(inc(x))


if __name__ == "__main__":
    print("result", twice(lambda y: y, 3))
