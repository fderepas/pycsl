r"""Test 9072 -- u30 route #568 (expected PASS): CONTROL: an opaque `Any` method call in a function that observes
no attribute state keeps its frameless stub under `assigns \nothing`.
"""
# pycsl-expected: PASS
from typing import Any

#@ requires n >= 0
#@ ensures \result == n + 1
#@ assigns \nothing
def bump(o: Any, n: int) -> int:
    o.ping(n)
    return n + 1

if __name__ == "__main__":
    class P:
        def ping(self, n):
            return n
    print(bump(P(), 4))
