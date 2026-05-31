"""Test heapq.heappushpop_max L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import heapq  # noqa: F401


#@ requires True
#@ ensures True
def use_heappushpop_max(x: int) -> int:
    return heapq.heappushpop_max(x)


if __name__ == "__main__":
    pass
