r"""Test 6015 -- gen #37 route #404 (expected FAIL): NEW latent: `class K(metaclass=mk)` with `mk` a FUNCTION returning `[1]`, then `{K}` under `no_exception \all` (CPython TypeError; ill-typed in WhyML at base 4431ef86f). REFUSED (PYCSL-S1-UNMODELLED-BASE: a `metaclass=` keyword must name `type`, `abc.ABCMeta`, `enum.EnumMeta` or a file class).
"""
# pycsl-expected: FAIL
from typing import Any


def mk(name: str, bases: Any, ns: Any) -> Any:
    return [1]


class K(metaclass=mk):
    pass


#@ no_exception \all
def f() -> int:
    s = {K}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
