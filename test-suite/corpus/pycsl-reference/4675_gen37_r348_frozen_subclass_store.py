r"""Test 4675 -- gen #37 route #348 (expected FAIL): (new) store on a plain subclass of a frozen dataclass; PROVED (CPython FrozenInstanceError). REFUSED (PYCSL-R348-IMMUTABLE-RECORD-STORE, route #348).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

@dataclass(frozen=True)
class D:
    x: int

class E(D):
    pass

#@ no_exception \all
#@ ensures \result == 5
def f(e: E) -> int:
    e.x = 5
    return e.x

if __name__ == "__main__":
    print(f(E(1)))
