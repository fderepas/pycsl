r"""Test 9229 -- route #575 CONTROL (expected PASS at base and HEAD): class objects used as what they are are admitted
while a module alias `AL = P` and a nested class `KN.Inner` are bound in the file: a dataclass constructed and tested
with `isinstance`, and an `Enum` CLASS iterated (its metaclass `EnumMeta` defines `__iter__`: route #575's
metaclass-`type` test does not resolve it, so it is not refused).
"""
# pycsl-expected: PASS
from dataclasses import dataclass
import enum


@dataclass
class P:
    a: int


class KN:
    class Inner:
        b: int = 0


class Color(enum.Enum):
    R = 1
    G = 2


AL = P


#@ no_exception \all
def f1(k: int) -> int:
    q = P(k)
    return q.a


#@ no_exception \all
def f2(p: P) -> int:
    return 1 if isinstance(p, P) else 0


#@ no_exception \all
def f3(k: int) -> int:
    t = 0
    for m in Color:
        t += 1
    return t


if __name__ == "__main__":
    print(f1(3), f2(P(1)), f3(0), AL is P, KN.Inner.b)
