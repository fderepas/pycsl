r"""Test 4686 -- gen #37 route #346: CONTROL: `__post_init__` on a dataclass WITHOUT an invariant, `no_exception` read; PROVES (CPython 3).
"""
from dataclasses import dataclass

@dataclass
class D:
    x: int
    def __post_init__(self) -> None:
        pass

#@ no_exception \all
def f(d: D) -> int:
    return d.x

if __name__ == "__main__":
    print(f(D(3)))
