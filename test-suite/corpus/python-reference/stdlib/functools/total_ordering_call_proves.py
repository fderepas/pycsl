"""Test functools.total_ordering L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import functools  # noqa: F401


#@ requires True
#@ ensures True
def use_total_ordering(x: int) -> int:
    return functools.total_ordering(x)


if __name__ == "__main__":
    pass
