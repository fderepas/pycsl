"""Test heapq.nlargest L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import heapq  # noqa: F401


#@ requires True
#@ ensures True
def use_nlargest(x: int) -> int:
    return heapq.nlargest(x)


if __name__ == "__main__":
    pass
