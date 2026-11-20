r"""Test 10279 -- run #8 u57, route #429 (expected PASS): over-refusal CONTROL: non-Latin-1 characters in DOCSTRINGS (module 😀, function €, class 😀) that the model never reads are not refused; the ASCII claim still proves.
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple


class C:
    """A class docstring: 😀"""
    pass


#@ ensures \result == 0
#@ assigns \nothing
def f(x: str) -> int:
    """A function docstring: \u20ac 😀"""
    if x == "ab":
        if len(x) == 2:
            return 0
        return 1
    return 0


if __name__ == "__main__":
    r = f("ab")
    print("VIOLATION contract" if r != 0 else "result", r)
