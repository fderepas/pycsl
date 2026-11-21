r"""Test 3162 — gen #37 ch27 (expected FAIL): REGRESSION GUARD for the receiver-dropped `.get`.
Outside the hval/emit_ir recognizers, `(<expr>).get(k, D)` on a typed `Dict[str, int]` lowers to
`get_2 <hash k> <hash D>`, which never mentions the receiver. That is sound ONLY because `get_2` is
a program `val` (a fresh unconstrained result per call). Were it ever made a `val function`, the
two reads below would be one term and `\result == 0` would PROVE, while CPython
`diff({"x": 1}, {})` is 1. Must stay UNPROVED.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == 0
#@ assigns \nothing
def diff(a: Dict[str, int], b: Dict[str, int]) -> int:
    return (a or {}).get("x", 0) - (b or {}).get("x", 0)


if __name__ == "__main__":
    print(diff({"x": 1}, {}))
