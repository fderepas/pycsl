r"""Test 4884 -- gen #37 route #362: CONTROL: `InitVar` dataclass WITHOUT an invariant, `no_exception` read of a real field; PROVES (CPython 1).
"""
from dataclasses import dataclass, InitVar

@dataclass
class D:
    x: int
    k: InitVar[int] = 0

#@ no_exception \all
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    print(f(D(1)))
