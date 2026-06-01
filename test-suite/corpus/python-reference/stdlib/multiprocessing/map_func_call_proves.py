"""Test multiprocessing.map_func L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_map_func(x: int) -> int:
    return multiprocessing.map_func(x)


if __name__ == "__main__":
    pass
