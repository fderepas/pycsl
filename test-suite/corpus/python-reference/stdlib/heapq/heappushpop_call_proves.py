"""Test heapq.heappushpop L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import heapq  # noqa: F401


#@ requires True
#@ ensures True
def use_heappushpop(x: int) -> int:
    return heapq.heappushpop(x)


if __name__ == "__main__":
    pass
