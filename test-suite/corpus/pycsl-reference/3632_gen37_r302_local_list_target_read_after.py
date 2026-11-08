r"""Test 3632 -- gen #37 route #302 (expected FAIL): a loop over a LOCAL list literal (`xs = [1, 2, 3]`), target read after, kept the pre-loop 0; CPython g() == 3.
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ ensures \result == 0
#@ assigns \nothing
def g() -> int:
    xs = [1, 2, 3]
    x = 0
    for x in xs:
        pass
    return x

if __name__ == "__main__":
    assert g() == 3
