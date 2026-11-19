r"""Test 3282 — gen #37 dict-value-wall Step 0, R5 (expected PASS): honest CONTROL for 3280/3281.
The outer value is the EMPTY dict (falsy), so `(rec.get("prover-result") or {})` is `{}` and
`.get("answer", "")` is "" — no exception, CPython "". The map assertion added to the
receiver-form `.get` under `no_exception` holds (the receiver select is `HMap PNil`), so the
repair does not refuse a receiver that really is a map.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == ""
#@ assigns \nothing
#@ no_exception \all
def answer() -> str:
    rec: Dict[str, PyVal] = {"prover-result": {}}
    return (rec.get("prover-result") or {}).get("answer", "") or ""


if __name__ == "__main__":
    assert answer() == ""
    print("ok")
