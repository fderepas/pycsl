r"""Test 5510 -- gen #37 route #383 allow-list addendum (expected PASS): CONTROL: `int` / `str` / `Tuple[str, str]` / `Optional[str]` values in a set display and a `str` dict key (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Tuple, Optional

#@ no_exception \all
#@ ensures \result == 1
def g(i: int, k: str, t: Tuple[str, str], o: Optional[str]) -> int:
    u = {i, k, t, o}
    m = {k: 1}
    return 1

if __name__ == "__main__":
    print(g(1, "a", ("a", "b"), None))
