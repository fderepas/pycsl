r"""Test 5501 -- gen #37 route #383 allow-list addendum (expected FAIL): `m: Dict[str, Any]`, `{m["a"]}` with a list value (CPython TypeError; PROVED at base b62ff2e23). REFUSED (PYCSL-R349-UNHASHABLE-RECORD).
"""
# pycsl-expected: FAIL
from typing import Any, Dict

#@ no_exception \all
#@ ensures \result == 1
def g(m: Dict[str, Any]) -> int:
    s = {m["a"]}
    return 1

if __name__ == "__main__":
    print(g({"a": [1]}))
