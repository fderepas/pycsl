"""Test bisect.bisect_left L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import bisect  # noqa: F401


#@ requires True
#@ ensures True
def use_bisect_left(x: int) -> int:
    return bisect.bisect_left(x)


if __name__ == "__main__":
    pass
