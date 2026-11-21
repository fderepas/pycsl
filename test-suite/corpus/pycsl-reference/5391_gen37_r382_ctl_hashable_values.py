r"""Test 5391 -- gen #37 route #382 (expected PASS): CONTROL: hashable values Tuple / FrozenSet / int / str / bytes / Optional[int], loop over List[int] (CPython ok).
"""
# pycsl-expected: PASS
from typing import Tuple, FrozenSet, List, Dict, Optional

#@ no_exception \all
#@ ensures \result == 1
def g(t: Tuple[int, str], f: FrozenSet[int], n: int, s: str, b: bytes, o: Optional[int],
      xs: List[int], m: Dict[str, int]) -> int:
    u = {t, f, n, s, b, o}
    for x in xs:
        u2 = {x}
    return 1

if __name__ == "__main__":
    print(g((1, "a"), frozenset([1]), 1, "s", b"b", None, [1, 2], {"a": 1}))
