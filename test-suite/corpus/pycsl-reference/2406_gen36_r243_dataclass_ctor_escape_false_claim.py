r"""Test 2306 — gen #36 r243 (expected FAIL): route #243: the dataclass constructor stores its argument into the field (`init_body`), the
caller keeps `x`, a method stores through the field, the caller reads `x`. CPython returns
True; PROVED at cdac19a6, now REFUSED at `C(x)`.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import Dict


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    d: Dict[int, int] = field(default_factory=dict)

    #@ assigns self.d
    def put(self) -> None:
        self.d[1] = 5


#@ ensures \result == False
def f() -> bool:
    x: Dict[int, int] = {}
    c = C(x)
    c.put()
    return 1 in x


if __name__ == "__main__":
    assert f() is True
