r"""Test 4671 -- gen #37 route #348 (expected FAIL): witness j03: frozen dataclass store in a free function; PROVED (CPython FrozenInstanceError). REFUSED (PYCSL-R348-IMMUTABLE-RECORD-STORE, route #348).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass(frozen=True)
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 5
def f(d: D) -> int:
    d.x = 5
    return d.x

if __name__ == "__main__":
    print(f(D(1)))
