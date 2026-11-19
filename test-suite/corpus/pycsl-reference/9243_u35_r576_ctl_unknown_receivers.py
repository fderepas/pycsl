r"""Test 9243 -- route #576 CONTROL (expected PASS at base and HEAD): the str VALUES route #576 now kinds as receivers -- a
record field `p.s`, a str method CALL result `p.s.upper()`, a computed str `p.s + "x"` and a local bound to the field --
searched for a str needle are admitted: route #576 refuses only an attribute of such a value that is a method / number /
absent, never the value itself.
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class P:
    a: int
    s: str


#@ no_exception \all
def f1(c: str, p: P) -> int:
    t = p.s
    return 1 if c in p.s or c in p.s.upper() or c in (p.s + "x") or c in t else 0


if __name__ == "__main__":
    print(f1("q", P(1, "q")))
