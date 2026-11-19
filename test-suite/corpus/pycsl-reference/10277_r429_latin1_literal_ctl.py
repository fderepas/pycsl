r"""Test 10277 -- run #8 u57, route #429 (expected PASS): over-refusal CONTROL: a LATIN-1 literal (`x == "\xe9\xff"`, code points 233 / 255, one string.Char each) => `len(x) == 2 and x[-1:] == "\xff"` (true) still proves.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple

#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    if x == "\xe9\xff":
        if len(x) == 2 and x[-1:] == "\xff":
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f("\xe9\xff")
    print("VIOLATION contract" if r != 0 else "result", r)
