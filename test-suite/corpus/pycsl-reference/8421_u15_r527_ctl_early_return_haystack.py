r"""Test 8421 -- route #527 (control, expected PASS): `if r.s is None: return 0` then `"a" in r.s` (early-return narrowing); CPython returns 0 / 1
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
    if r.s is None:
        return 0
    return 1 if "a" in r.s else 2


if __name__ == "__main__":
    print("result", f(R(None, "ab")), f(R("abc", "ab")))
