r"""Test 3292 — gen #37 dict-value-wall Step 1 / R2a (expected PASS): the present key sits BEHIND a non-matching binding.
A dict literal builds its assoc list by PREPENDING, so `{"answer": "Valid", "goal": "g1"}` is
`PCons "goal" .. (PCons "answer" .. PNil)`: the read must first decide `"answer" <> "goal"`
(literal distinctness). The review measured alt-ergo cannot separate string literals there; z3 (in
pycsl's default portfolio) can. CPython "Valid". Twin: 3293.
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "Valid"
#@ assigns \nothing
def answer() -> str:
    rec: Dict[str, PyVal] = {"prover-result": {"answer": "Valid", "goal": "g1"}}
    return (rec.get("prover-result") or {}).get("answer", "") or ""


if __name__ == "__main__":
    assert answer() == "Valid"; print("ok")
