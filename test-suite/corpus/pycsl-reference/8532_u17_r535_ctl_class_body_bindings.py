r"""Test 8532 -- route #535 (control, expected PASS): a dataclass whose class body binds names OTHER than its builtin factories (a ClassVar `size`, a method `total`) and a module-scope binding of an unrelated name; the factories `list` / `dict` are the builtins; CPython f(5) returns 5
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import ClassVar, Dict, List

LIMIT = 3


@dataclass
class P:
    size: ClassVar[int] = 2
    a: int
    xs: List[int] = field(default_factory=list)
    m: Dict[int, int] = field(default_factory=dict)

    def total(self) -> int:
        return self.a


#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    p = P(n)
    return p.a


if __name__ == "__main__":
    print(f(5))
