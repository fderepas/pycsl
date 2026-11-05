r"""Test 8823 -- lvA re.sub callable repl (expected FAIL): false twin of 8822. The callable result is an
ARBITRARY string to the model (plain `val`, no content law), so `\result == s` must NOT prove
(CPython: upper-casing "a" gives "A").
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re


#@ ensures \result == s
#@ assigns \nothing
def upper_a(s: str) -> str:
    p = re.compile(r"a")
    return p.sub(lambda m: m.group(0).upper(), s)


if __name__ == "__main__":
    r = upper_a("a")
    print("VIOLATION contract" if r != "a" else "result", r)
