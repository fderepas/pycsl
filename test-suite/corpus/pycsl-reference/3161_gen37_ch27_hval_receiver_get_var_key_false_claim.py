r"""Test 3161 — gen #37 ch27 (expected FAIL): FALSE twin of 3160. The record carries
`{"a": {"x": "v"}}` and the key is the PARAMETER `k`: CPython `answer_of("x")` returns "v", so
`\result == ""` must stay UNPROVED. A lowering that dropped the receiver (or the key) and answered
the default would prove it.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == ""
#@ assigns \nothing
def answer_of(k: str) -> str:
    rec: Dict[str, PyVal] = {"a": {"x": "v"}}
    return (rec.get("a") or {}).get(k, "") or ""


if __name__ == "__main__":
    print(repr(answer_of("x")))
