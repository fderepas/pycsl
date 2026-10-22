r"""Test 3538 — gen #37 ch31 (expected PASS): `"a" in rec["fields"]` where `rec["fields"]` is a dict
(`HMap`) tests KEY presence (CPython: 1). At 0f7cb454 the subscript arm used `hval_str_mem`, which
reads False on every non-list carrier (a model-level false claim, spike `head_in_map`).
"""
from typing import Any, Dict

PyVal = Any


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    rec: Dict[str, PyVal] = {"fields": {"a": 1}}
    if "a" in rec["fields"]:
        return 1
    return 2


if __name__ == "__main__":
    print(g())
