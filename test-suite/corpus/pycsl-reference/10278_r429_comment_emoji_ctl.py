r"""Test 10278 -- run #8 u57, route #429 (expected PASS): over-refusal CONTROL: a non-Latin-1 character in a COMMENT (😀, €) does not enter the model and is not refused; the ASCII claim still proves.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple

# a comment with characters above Latin-1: 😀 € \u0301
#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    # 😀 inside the body too
    if x == "ab":  # trailing 😀
        if len(x) == 2:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f("ab")
    print("VIOLATION contract" if r != 0 else "result", r)
