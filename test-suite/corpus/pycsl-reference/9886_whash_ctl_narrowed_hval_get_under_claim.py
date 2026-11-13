r"""Test 9886 -- W-hash (dict-value-model-r4 §2.5, expected PASS): CONTROL: an `hval` read (`d.get("a")` of a `Dict[str, PyVal]`) narrowed by `isinstance(v, str)` and then hashed under `no_exception \all` is admitted and PROVES. REFUSED at base by route R-gate (no narrowing was read).
"""
# pycsl-expected: PASS
from typing import Any, Dict

PyVal = Any


#@ no_exception \all
#@ ensures \result == n + 1
def f(n: int) -> int:
    d: Dict[str, PyVal] = {"a": "s"}
    v = d.get("a")
    if isinstance(v, str):
        s = {v}
        return n + 1
    return n + 1


if __name__ == "__main__":
    print(f(0))
