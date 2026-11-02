r"""Test 8420 -- route #527 (control, expected PASS): `if r.s is not None: w = r.s + "x"` (flow narrowing); CPython returns 0 / 1
"""
# pycsl-expected: PASS
from typing import Optional
from dataclasses import dataclass


@dataclass
class R:
    s: Optional[str]
    t: str


#@ no_exception \all
def f(r: R) -> int:
    if r.s is not None:
        w = r.s + "x"
        return 1
    return 0


if __name__ == "__main__":
    print("result", f(R(None, "ab")), f(R("q", "ab")))
