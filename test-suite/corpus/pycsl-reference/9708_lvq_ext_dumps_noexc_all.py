r"""Test 9708 -- lvQ open-world model (expected FAIL): `json.dumps` raises ValueError (a circular
structure) and TypeError (a non-serialisable value); under `no_exception \all` the call must NOT
verify.
"""
# pycsl-expected: FAIL
from __future__ import annotations
import json


#@ no_exception \all
#@ ensures \result == 0
#@ assigns \nothing
def dump(payload: dict) -> int:
    s = json.dumps(payload, indent=2)
    return 0


if __name__ == "__main__":
    d = {}
    d["self"] = d
    try:
        dump(d)
        print("result ok")
    except ValueError as e:
        print("VIOLATION no_exception", e)
