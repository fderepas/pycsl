r"""Test 3523 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. `len({"x", a})` with a == "x": CPython 1; the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 2
#@ assigns \nothing
def f(a: str) -> int:
    s = {"x", a}
    return len(s)

if __name__ == "__main__":
    # CPython ground truth: the claimed value is NOT what the program returns.
    assert f("x") != 2, f("x")
