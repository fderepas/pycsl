r"""Test 8486 -- route #539 (control, expected PASS): a module global bound ONCE to a constant keeps that kind in a constructor: `n + K` with `K = 1`; CPython f(2) returns 2. (Integration note, driver run #4: the `default_factory=lambda: K + 1` half of this control is refused once route #534 lands beside it -- #534 judges factory-lambda bodies by LITERAL kinds and admits no name; that over-refusal is recorded in route534 / route539.)
"""
# pycsl-expected: PASS
import dataclasses
from typing import Any

K = 1


@dataclasses.dataclass
class P:
    a: int
    b: Any = dataclasses.field(default_factory=lambda: 1 + 1)


class Q:
    def __init__(self, n: int) -> None:
        self.k = n + K


#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    p = P(n)
    q = Q(n)
    return p.a


if __name__ == "__main__":
    print(f(2))
