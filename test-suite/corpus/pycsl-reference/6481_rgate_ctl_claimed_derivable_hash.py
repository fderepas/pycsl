r"""Test 6481 -- route R-gate (expected PASS): CONTROL: claimed (`no_exception \all`) functions hashing DERIVABLE values -- a `Dict[str, int]` value via `.get` with a default, a `str` parameter, a tuple of typed values, an `int` arithmetic key `k + 1` with `k` iterating `list(d.keys())` (`d: Dict[int, int]`; the `list(x)` element derivation added for control 6336) -- are not refused. PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Dict, Set, Tuple


#@ no_exception \all
#@ ensures \result == n + 1
def f(m: Dict[str, int], seen: Set[int], n: int) -> int:
    seen.add(m.get("a", 0))
    return n + 1


#@ no_exception \all
#@ ensures \result == n + 1
def g(name: str, seen: Set[str], n: int) -> int:
    s = {name}
    seen.add(name)
    return n + 1


#@ no_exception \all
#@ ensures \result == n + 1
def h(a: int, b: str, n: int) -> int:
    t: Set[Tuple[int, str]] = set()
    t.add((a, b))
    return n + 1


#@ no_exception \all
#@ ensures \result == n + 1
def kk(d: Dict[int, int], n: int) -> int:
    for k in list(d.keys()):
        d[k + 1] = 0
    return n + 1


if __name__ == "__main__":
    print(f({"a": 1}, set(), 0), g("n", set(), 0), h(1, "b", 0), kk({1: 1}, 0))
