r"""Test 8531 -- route #534 (control, expected PASS): parameterless factory lambdas whose literal operands are of matching kinds -- `"a" + "b"`, `1 + 2`, `[1] + [2]`, `(1,) + (2,)`, `{1, 2}`, `{"a": [1]}`, `1 < 2`, `1 in [1]`, `"a" in "ab"`, `-1`, `~1`, `"abc"[1:]`, `[0] * 4`, `f"{1}"`, `list()`; CPython f(5) returns 5
"""
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import Any


@dataclass
class P:
    a: int
    b: Any = field(default_factory=lambda: "a" + "b")
    c: Any = field(default_factory=lambda: 1 + 2)
    d: Any = field(default_factory=lambda: [1] + [2])
    e: Any = field(default_factory=lambda: (1,) + (2,))
    g: Any = field(default_factory=lambda: {1, 2})
    h: Any = field(default_factory=lambda: {"a": [1]})
    i: Any = field(default_factory=lambda: 1 < 2)
    j: Any = field(default_factory=lambda: 1 in [1])
    k: Any = field(default_factory=lambda: "a" in "ab")
    m: Any = field(default_factory=lambda: -1)
    o: Any = field(default_factory=lambda: ~1)
    q: Any = field(default_factory=lambda: "abc"[1:])
    r: Any = field(default_factory=lambda: [0] * 4)
    s: Any = field(default_factory=lambda: f"{1}")
    t: Any = field(default_factory=lambda: list())


#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    p = P(n)
    return p.a


if __name__ == "__main__":
    print(f(5))
