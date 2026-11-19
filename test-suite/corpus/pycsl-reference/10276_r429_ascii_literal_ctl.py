r"""Test 10276 -- run #8 u57, route #429 (expected PASS): over-refusal CONTROL: an ASCII literal, `x == "abc"` => `len(x[:-1]) == 2 and x[-1:] == "c"` (true) still proves.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple

#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    if x == "abc":
        if len(x[:-1]) == 2 and x[-1:] == "c":
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f("abc")
    print("VIOLATION contract" if r != 0 else "result", r)
