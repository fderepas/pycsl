r"""Test 4941 -- gen #37 route #365 (expected PASS): CONTROL: tuples of a hashable frozen record in set / hash / dict-key positions prove (CPython ok).
"""
# pycsl-expected: PASS
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class F:
    x: int
    t: Tuple[int, str]

#@ no_exception \all
#@ ensures \result == 1
def g(f: F, u: Tuple[F, int]) -> int:
    s = {(f, 1)}
    h = hash((f, 2))
    m = {u: 0}
    return 1

if __name__ == "__main__":
    print(g(F(1, (2, "a")), (F(1, (2, "b")), 3)))
