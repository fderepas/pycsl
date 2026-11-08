r"""Test 3286 — gen #37 dict-value-wall (expected FAIL): the DOUBLED one-argument read
`rec["a"].get("x")` mapped a present NON-string value to `None` and then to "", so over
`{"a": {"x": 5}}` it PROVED `\result == ""` on land27 (CPython returns 5). Found re-running the hval
false twins for R2a; it proves on land27 7966cfe2 WITHOUT R2a (both arms answered ""). A present
value now projects through `hstr_of`, whose non-string arm is the opaque `hval_opaque_str`.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == ""
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"a": {"x": 5}}
    return rec["a"].get("x")


if __name__ == "__main__":
    print(repr(answer()))
