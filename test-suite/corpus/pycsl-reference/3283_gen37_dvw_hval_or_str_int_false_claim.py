r"""Test 3283 — gen #37 dict-value-wall Step 0, R6 (expected FAIL): red-team round 7 p083.
`<hval> or "<lit>"` lowered to `if hval_truthy v then hstr_of v else lit`, and `hstr_of` maps every
non-`HStr` carrier to "". The value here is the INT 5 (truthy), so CPython returns 5 and
`\result == ""` is FALSE; it PROVED in land27. Now a truthy non-string operand is an OPAQUE string
(`hval_opaque_str v`, uninterpreted, no spec), never "".
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == ""
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"answer": 5}
    return rec.get("answer") or ""


if __name__ == "__main__":
    print(repr(answer()))
