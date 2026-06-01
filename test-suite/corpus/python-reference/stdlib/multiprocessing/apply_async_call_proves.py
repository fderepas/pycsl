"""Test multiprocessing.apply_async L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_apply_async(x: int) -> int:
    return multiprocessing.apply_async(x)


if __name__ == "__main__":
    pass
