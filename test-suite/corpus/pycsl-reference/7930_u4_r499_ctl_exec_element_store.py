r"""Test 7930 -- route #499 (control, expected PASS): a constant `exec("xs[0] = 5")` in a function stores into the SAME list object CPython's snapshot holds; spliced, still proves; CPython 5
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


#@ ensures \result == 5
def f(n: int) -> int:
    xs: List[int] = [1, 2]
    exec("xs[0] = 5")
    return xs[0]


if __name__ == "__main__":
    assert f(0) == 5
