r"""Test 4363 -- gen #37 route #330 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION BARE-CONTAINER-INT): an element of a bare `xs: List` is read as an int, so `xs[0] % 1 == 0` PROVES although CPython refutes it for `[0.5]` (see `__main__`). The counterexample of the assumption, listed by `--soundness-report`; twin 4348 drops it.
"""
# pycsl-expected: PASS
from typing import List
#@ ensures \result == True
#@ assigns \nothing
def g(xs: List) -> bool:
    return xs[0] % 1 == 0

if __name__ == "__main__":
    assert g([0.5]) == True
