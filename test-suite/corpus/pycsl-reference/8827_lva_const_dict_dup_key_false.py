r"""Test 8827 -- lvA module-constant str-pair loops (expected FAIL): false twin of 8826. A dict literal
with a DUPLICATE key keeps the LAST value ("a" -> "cc"), so the length is NOT preserved and the claim
must NOT prove (CPython: rewrite("a") is False: "a" -> "cc"). An unroll that kept the first value would prove it.
"""
# pycsl-expected: FAIL
from __future__ import annotations

_OPS = {"a": "b", "a": "cc"}


#@ ensures \result == True
#@ assigns \nothing
def rewrite(s: str) -> bool:
    out = s.strip()
    n = len(out)
    for k, v in _OPS.items():
        out = out.replace(k, v)
    return len(out) == n


if __name__ == "__main__":
    r = rewrite("a")
    print("VIOLATION contract" if r is not True else "result", r)
