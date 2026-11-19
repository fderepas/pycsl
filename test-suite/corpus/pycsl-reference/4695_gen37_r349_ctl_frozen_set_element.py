r"""Test 4695 -- gen #37 route #349: CONTROL: frozen dataclass in a set; PROVES (CPython 1).
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
