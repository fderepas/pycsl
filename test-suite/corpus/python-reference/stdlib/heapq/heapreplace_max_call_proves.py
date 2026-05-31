"""Test heapq.heapreplace_max L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import heapq  # noqa: F401


#@ requires True
#@ ensures True
def use_heapreplace_max(x: int) -> int:
    return heapq.heapreplace_max(x)


if __name__ == "__main__":
    pass
