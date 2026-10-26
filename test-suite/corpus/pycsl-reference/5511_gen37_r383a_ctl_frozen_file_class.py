r"""Test 5511 -- gen #37 route #383 allow-list addendum (expected PASS): CONTROL: a frozen file dataclass in a set display (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from dataclasses import dataclass

@dataclass(frozen=True)
class K:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(k: K) -> int:
    s = {k}
    return 1

if __name__ == "__main__":
    print(g(K(1)))
