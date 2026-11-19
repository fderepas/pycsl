r"""Test 7931 -- route #499 (control, expected PASS): a MODULE-level constant `exec("y = 6")` binds the real global namespace (the splice is inline-equivalent there); CPython 6
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


exec("y = 6")


#@ ensures \result == 6
#@ assigns \nothing
def f() -> int:
    return y


if __name__ == "__main__":
    assert f() == 6
