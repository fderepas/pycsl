"""Test bisect.insort_right L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import bisect  # noqa: F401


#@ requires True
#@ ensures True
def use_insort_right(x: int) -> int:
    return bisect.insort_right(x)


if __name__ == "__main__":
    pass
