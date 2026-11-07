r"""Test 8826 -- lvA module-constant str-pair loops (expected PASS): `for k, v in _OPS.items()` over a
module constant str->str dict literal and `for a, b in _STRIPS` over a module constant list of str
2-tuples are UNROLLED over the real pairs (`module_const_str_pairs`), so each `.replace` gets literal
arguments. Every pair has equal-length strings, so the faithful `str_replace_op` length law keeps the
length. At base the tuple targets were `any int` and the body did not type-check. Twin: 8827.
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List, Tuple

_OPS = {"<=": ">=", "->": "=>", "/\\": "\\/"}
_STRIPS: List[Tuple[str, str]] = [("Nat.gcd", "Zgcd__x"), ("ab", "cd")]


#@ ensures \result == True
#@ assigns \nothing
def rewrite(s: str) -> bool:
    out = s.strip()
    n = len(out)
    for k, v in _OPS.items():
        out = out.replace(k, v)
    for a, b in _STRIPS:
        out = out.replace(a, b)
    return len(out) == n


if __name__ == "__main__":
    for s in ["a <= b -> c", "Nat.gcd ab", ""]:
        r = rewrite(s)
        print("VIOLATION contract" if r is not True else "result", r)
