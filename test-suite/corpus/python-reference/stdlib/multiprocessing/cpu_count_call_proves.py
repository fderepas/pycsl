"""Test multiprocessing.cpu_count L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_cpu_count(x: int) -> int:
    return multiprocessing.cpu_count(x)


if __name__ == "__main__":
    pass
