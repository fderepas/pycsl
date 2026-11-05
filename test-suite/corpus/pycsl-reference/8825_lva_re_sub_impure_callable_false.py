r"""Test 8825 -- lvA re.sub callable repl (expected FAIL): a lambda that reads a FREE variable and MUTATES it
(`xs.pop()`) is not a closed pure callable, so the callable model must NOT apply (were it applied, the
lambda body would be dropped and `len(xs) == 3` would follow from the untouched list). CPython: one match
pops one element, so run("a", [1, 2, 3]) leaves `len(xs) == 2`.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re
from typing import List


#@ requires len(xs) == 3
#@ ensures len(xs) == 3
#@ assigns xs
def run(s: str, xs: List[int]) -> str:
    return re.sub(r"a", lambda m: str(xs.pop()), s)


if __name__ == "__main__":
    xs = [1, 2, 3]
    run("a", xs)
    print("VIOLATION contract" if len(xs) != 3 else "result", len(xs))
