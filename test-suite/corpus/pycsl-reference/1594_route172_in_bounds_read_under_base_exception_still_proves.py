r"""Test 1594 - ROUTE #172 control (gen #29), superseded by ROUTE #174: an in-bounds read inside a try with `except BaseException` proved `\result == 2` under #172; a broad handler can also be reached by exceptions the model does not raise (AttributeError, OverflowError, ...), so route #174 refuses it in a claiming function.
"""
# pycsl-expected: FAIL
from typing import List
_ = 0  # anchor


#@ ensures \result == 2
def probe() -> int:
    xs: List[int] = [1, 2]
    try:
        v = xs[1]
    except BaseException:
        return 9
    return v
