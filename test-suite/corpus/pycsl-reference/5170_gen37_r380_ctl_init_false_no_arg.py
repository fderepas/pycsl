r"""Test 5170 -- gen #37 route #380 (expected PASS): CONTROL: `@dataclass(init=False)` with a defaulted field constructed `D()`: `object.__init__` takes no argument, `d.x == 4` (CPython ok).
"""
# pycsl-expected: PASS
from dataclasses import dataclass

@dataclass(init=False)
class D:
    x: int = 4

#@ no_exception \all
#@ ensures \result == 4
def f() -> int:
    d = D()
    return d.x

if __name__ == "__main__":
    print(f())
