r"""Test 2910 — route #271 CONTROL (expected PASS): a generator carrying only `requires` and
`assigns` (no claim about an eager run) is accepted while nothing calls it; the ordinary
function beside it still proves. CPython `h(2)` = 3.
"""
# pycsl-expected: PASS
from typing import Iterator

#@ requires n >= 0
#@ assigns \nothing
def count(n: int) -> Iterator[int]:
    yield n

#@ requires n >= 0
#@ ensures \result == n + 1
#@ assigns \nothing
def h(n: int) -> int:
    return n + 1

if __name__ == "__main__":
    print(h(2), list(count(2)))
