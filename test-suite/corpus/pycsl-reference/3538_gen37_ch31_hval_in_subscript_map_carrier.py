r"""Test 3538 — gen #37 ch31 (expected PASS): `"a" in rec["fields"]` where `rec` is an hval LOCAL
and `rec["fields"]` is a dict (`HMap`) tests KEY presence (CPython: 1). At 0f7cb454 the
`_typeddict_field_access` subscript arm used `hval_str_mem`, which reads False on every non-list
carrier: this claim timed out and its twin 3539 PROVED (a false proof).
"""
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    holder: Dict[str, PyVal] = {"r": {"fields": {"a": 1}}}
    rec = holder.get("r")
    if "a" in rec["fields"]:
        return 1
    return 2


if __name__ == "__main__":
    print(g())
