"""Test multiprocessing.map_async L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_map_async(x: int) -> int:
    return multiprocessing.map_async(x)


if __name__ == "__main__":
    pass
