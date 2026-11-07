r"""Test 8562 -- route #540 (control, expected PASS): `+r.n` of an `Optional[int]` field under `if r.n is not None:` (flow narrowing); CPython returns 0 / 1
"""
# pycsl-expected: PASS
from typing import Optional
from dataclasses import dataclass


@dataclass
class R:
    n: Optional[int]


#@ no_exception \all
def f(r: R) -> int:
    if r.n is not None:
        w = +r.n
        return 1
    return 0


if __name__ == "__main__":
    print("result", f(R(None)), f(R(4)))
