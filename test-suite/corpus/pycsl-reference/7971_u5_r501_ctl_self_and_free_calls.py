r"""Test 7971 -- route #501 (control, expected PASS): methods call each other through `self`, and a free def `sqrt` is called by name; the caller method catches ValueError; `ensures \result == 3`; CPython C().b(2) returns 3
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

#@ ensures \result == x + 1
def sqrt(x: int) -> int:
    return x + 1


class C:
    #@ ensures \result == x + 1
    def a(self, x: int) -> int:
        return sqrt(x)

    #@ ensures \result == x + 1
    def b(self, x: int) -> int:
        try:
            return self.a(x)
        except ValueError:
            return 0


if __name__ == "__main__":
    assert C().b(2) == 3
