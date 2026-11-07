r"""Test 6462 -- route #430 (expected FAIL): the #430 shape through a MEMBERSHIP test: a `no_exception \all` function calls `h(m, s, n)`, an un-claimed callee that tests `m.get("a") in s` (`s: Set[str]`, `m: Dict[str, Any]`: the underivable value is hashed by the set lookup). PROVED at base 725a1c7e5; CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED.
"""
# pycsl-expected: FAIL
from typing import Dict, Any, Set


#@ ensures \result >= n
def h(m: Dict[str, Any], s: Set[str], n: int) -> int:
    if m.get("a") in s:
        return n + 1
    return n


#@ no_exception \all
#@ ensures \result >= n
def caller(m: Dict[str, Any], s: Set[str], n: int) -> int:
    return h(m, s, n)


if __name__ == "__main__":
    try:
        print(caller({"a": [1]}, set(), 0))
    except TypeError:
        print("VIOLATION: TypeError under no_exception \\all")
