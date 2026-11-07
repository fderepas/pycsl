r"""Test 1624 - ROUTE #177 control (gen #29): a comprehension with no raising operation (`[x + 1 for x in xs]`) under `#@ no_exception ZeroDivisionError` still proves.
"""
from typing import List
_ = 0  # anchor


#@ no_exception ZeroDivisionError
#@ ensures \result == 5
def probe() -> int:
    xs: List[int] = [0, 1]
    ys = [x + 1 for x in xs]
    return 5
