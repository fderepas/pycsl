r"""Test 4693 -- gen #37 route #348: CONTROL: store on a MUTABLE dataclass; PROVES (CPython 5).
"""
from dataclasses import dataclass

@dataclass
class D:
    x: int

#@ no_exception \all
#@ ensures \result == 5
def f(d: D) -> int:
    d.x = 5
    return d.x

if __name__ == "__main__":
    print(f(D(1)))
