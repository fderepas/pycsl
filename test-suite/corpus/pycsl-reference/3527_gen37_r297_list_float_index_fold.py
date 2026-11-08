r"""Test 3527 -- gen #37 route #297 (expected FAIL): the compile-time collection-literal fold
must not answer from the literal's source text. `a = [4, 5]; a[1.0]`: CPython TypeError (the fold truncated the float index); the claim is FALSE of the program.
"""
# pycsl-expected: FAIL
from typing import List, Dict, Set, Tuple, Optional

#@ ensures \result == 5
#@ assigns \nothing
def f() -> int:
    a: List[int] = [4, 5]
    return a[1.0]

if __name__ == "__main__":
    try:
        f()
        raise SystemExit("expected TypeError")
    except TypeError:
        pass
