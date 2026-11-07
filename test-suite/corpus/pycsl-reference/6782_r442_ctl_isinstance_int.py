r"""Test 6782 -- route #442 (expected PASS): CONTROL -- `isinstance(x, int)` (a resolved builtin class) narrows `Optional[int]` before `x.bit_length()`; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Optional


#@ no_exception \all
def f(x: Optional[int]) -> int:
    if isinstance(x, int):
        return x.bit_length()
    return 0


if __name__ == "__main__":
    print("result", f(5), f(None))
