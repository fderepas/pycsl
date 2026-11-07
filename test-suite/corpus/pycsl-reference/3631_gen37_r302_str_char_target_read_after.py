r"""Test 3631 -- gen #37 route #302 (expected FAIL): the char-iteration lowering (`for c in s`), target read after the loop, kept the pre-loop `""`; CPython g("q") == "q".
"""
# pycsl-expected: FAIL
from typing import Any, List, Dict, Set, Tuple, Optional

#@ requires len(s) == 1
#@ ensures \result == ""
#@ assigns \nothing
def g(s: str) -> str:
    c = ""
    for c in s:
        pass
    return c

if __name__ == "__main__":
    assert g("q") == "q"
