r"""Test 4694 -- gen #37 route #349: CONTROL: eq-dataclass with an explicit `__hash__` in a set; PROVES (CPython 1). Route #402: the `__hash__` a hashing site calls carries a verified `#@ no_exception \all` contract.
"""
from dataclasses import dataclass

@dataclass
class D:
    x: int
    #@ no_exception \all
    def __hash__(self) -> int:
        return 0

#@ no_exception \all
#@ ensures \result == 1
def g(d: D) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(D(1)))
