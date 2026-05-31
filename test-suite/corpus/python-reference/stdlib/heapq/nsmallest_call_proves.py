"""Test heapq.nsmallest L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import heapq  # noqa: F401


#@ requires True
#@ ensures True
def use_nsmallest(x: int) -> int:
    return heapq.nsmallest(x)


if __name__ == "__main__":
    pass
