r"""Test 8423 -- route #527 (control, expected PASS): the plain `str` field `r.t` beside an `Optional[str]` one: `r.t + "x"`, `"a" in r.t` are not judged; CPython returns 1
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
    w = r.t + "x"
    return 1 if "a" in r.t else 0


if __name__ == "__main__":
    print("result", f(R(None, "ab")))
