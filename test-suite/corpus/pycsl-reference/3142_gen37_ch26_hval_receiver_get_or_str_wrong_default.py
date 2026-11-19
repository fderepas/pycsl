r"""Test 3142 — gen #37 ch26 (expected FAIL): FALSE twin of 3140. A record without the outer key
answers the literal fallback "" (CPython: ""), never another string: `\result == "x"` must stay
UNPROVED (the `or "<lit>"` arm returns ITS literal, not an unconstrained string).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "x"
#@ assigns \nothing
def answer_of_empty() -> str:
    rec: Dict[str, PyVal] = {}
    return (rec.get("prover-result") or {}).get("answer", "") or ""


if __name__ == "__main__":
    print(repr(answer_of_empty()))
