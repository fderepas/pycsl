"""Test functools.wraps L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import functools  # noqa: F401


#@ requires True
#@ ensures True
def use_wraps(x: int) -> int:
    return functools.wraps(x)


if __name__ == "__main__":
    pass
