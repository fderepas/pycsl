"""Test heapq.heappush L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import heapq  # noqa: F401


#@ requires True
#@ ensures True
def use_heappush(x: int) -> int:
    return heapq.heappush(x)


if __name__ == "__main__":
    pass
