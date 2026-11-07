r"""Test 8304 -- route #520 (control, expected PASS): dataclass `default_factory` of a builtin container type and parameterless lambdas building a literal display / a small-literal repetition; CPython f() returns 1
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import List


@dataclass
class P:
    xs: List[int] = field(default_factory=list)
    ys: List[int] = field(default_factory=lambda: [1, 2, 3])
    zs: List[int] = field(default_factory=lambda: [0] * 4)


#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    p = P()
    return 1


if __name__ == "__main__":
    print(f())
