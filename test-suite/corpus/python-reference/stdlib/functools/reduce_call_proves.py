"""Test functools.reduce L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import functools  # noqa: F401


#@ requires True
#@ ensures True
def use_reduce(x: int) -> int:
    return functools.reduce(x)


if __name__ == "__main__":
    pass
