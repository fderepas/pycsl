r"""Test 8424 -- route #527 (control, expected PASS): `r.s + "x"` in a function with no `no_exception` claim (a TypeError only ends it abnormally, route #431) is not judged
"""
# pycsl-expected: PASS
from typing import Optional
from dataclasses import dataclass


@dataclass
class R:
    s: Optional[str]
    t: str


#@ ensures \result == len(r.t)
def f(r: R) -> int:
    w = r.s + "x"
    return len(r.t)


if __name__ == "__main__":
    print("result", f(R("q", "ab")))
