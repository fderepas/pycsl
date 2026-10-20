r"""Test 3287 — gen #37 dict-value-wall (expected FAIL): the DOUBLED one-argument read on a
MISSING key: CPython `{}.get("x")` is None, not "", yet land27 7966cfe2 PROVED `\result == ""`
(main does not: its hval readers were logic-opaque). The missing key now projects route #238's
`None` spelling `HInt pycsl_none` through `hstr_of` (opaque).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == ""
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"a": {}}
    return rec["a"].get("x")


if __name__ == "__main__":
    print(repr(answer()))
