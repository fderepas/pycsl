r"""Test 9596 -- route #590 WITNESS (expected FAIL: REFUSED PYCSL-R590-RAISE-NON-EXCEPTION at HEAD, every model; PROVED at base, rt56 ha1780): `raise E("a")` of a `@dataclass class E` (no exception base) lowered to a tag `E` and `except E` caught it. CPython raises TypeError ("exceptions must derive from BaseException").
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class E:
    m: str


#@ no_exception \all
#@ ensures \result == 1
def f(k: int) -> int:
    try:
        raise E("a")
    except E:
        return 1
    return 0


if __name__ == "__main__":
    try:
        print(f(0))
    except Exception as e:
        print("VIOLATION", type(e).__name__)
