r"""Test 9242 -- route #576 CONTROL (expected PASS at base and HEAD): the METHOD CALLS (not the method objects) of receivers
route #576 now kinds are admitted: `k in xs` beside `p.s.upper()` / `t2.upper()` / `(s + "x").upper()` used as values,
and a record FIELD named like a builtin method (`q.upper: str`, `q.keys: str`) searched for a str needle.
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    a: int
    s: str


@dataclass
class Q:
    upper: str
    keys: str


#@ no_exception \all
def f1(k: int, s: str, p: P) -> int:
    t2 = s.strip()
    u = p.s.upper()
    w = (s + "x").upper()
    v = t2.upper()
    return 1 if u == v and w == v else 0


#@ no_exception \all
def f2(c: str, q: Q) -> int:
    return 1 if c in q.upper or c in q.keys else 0


if __name__ == "__main__":
    print(f1(1, "ab", P(1, "q")), f2("a", Q("ab", "c")))
