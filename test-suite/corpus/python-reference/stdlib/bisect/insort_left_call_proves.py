"""Test bisect.insort_left L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import bisect  # noqa: F401


#@ requires True
#@ ensures True
def use_insort_left(x: int) -> int:
    return bisect.insort_left(x)


if __name__ == "__main__":
    pass
