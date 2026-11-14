r"""Test 9914 -- lvS (expected PASS): a `Dict[str, PyVal]` element bound to a local named like a WhyML
keyword (`rec`, declared `py_rec`) is read by `.get` through its WhyML name (the raw `rec` was a Why3
syntax error, fail-closed); the read is the real `pairs_get` projection, so the key-membership guard
makes `\result >= 0` provable. Twin: 9915 (must FAIL).
"""
# pycsl-expected: PASS
from typing import Any, Dict, List

PyVal = Any


#@ ensures \result >= 0
#@ assigns \nothing
def count_terms(records: List[Dict[str, PyVal]]) -> int:
    n = 0
    for rec in records:
        term = rec.get("term") or {}
        if term:
            n = n + 1
    return n


if __name__ == "__main__":
    print("result", count_terms([{"term": {"a": 1}}, {}, {"term": {}}]))
