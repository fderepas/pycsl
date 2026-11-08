r"""Test 8770 -- route #557 (control, expected PASS): a set used through its own operations (`add`, `discard`, membership) next to a dict whose item store is a map update; CPython 3
"""
# pycsl-expected: PASS
from typing import Dict, Set


#@ no_exception \all
def f(k: int, s: Set[int]) -> int:
    d: Dict[int, int] = {}
    d[k] = 1
    s.add(k)
    s.discard(k)
    return 1 if k in s else 3


if __name__ == "__main__":
    print(f(1, {1, 2}))
