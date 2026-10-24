r"""Test 4694 -- gen #37 route #349: CONTROL: eq-dataclass with an explicit `__hash__` in a set; PROVES (CPython 1).
"""
from dataclasses import dataclass

@dataclass
class D:
    x: int
    def __hash__(self) -> int:
        return 0

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
