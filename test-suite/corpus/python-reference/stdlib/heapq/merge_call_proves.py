"""Test heapq.merge L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import heapq  # noqa: F401


#@ requires True
#@ ensures True
def use_merge(x: int) -> int:
    return heapq.merge(x)


if __name__ == "__main__":
    pass
