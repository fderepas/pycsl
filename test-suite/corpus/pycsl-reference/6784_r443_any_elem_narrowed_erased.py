r"""Test 6784 -- route #443 (expected FAIL): an element of `List[Any]` bound to a local and narrowed by `isinstance(v, str)` is ADMITTED by #443 (no refusal); the erased value's own obligation (route #343: `len` of a method result on an erased value) then stays Unknown -- FAIL at base fa7cbb1aa and candidate. It pins that #443 narrows, and why its advice names a concrete source type, not narrowing.
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ no_exception \all
def f(xs: List[Any]) -> int:
    if len(xs) == 0:
        return 0
    v = xs[0]
    if isinstance(v, str):
        return len(v.strip())
    return 0


if __name__ == "__main__":
    print("result", f([1]), f([" a "]))
