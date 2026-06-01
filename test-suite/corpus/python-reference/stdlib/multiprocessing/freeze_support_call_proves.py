"""Test multiprocessing.freeze_support L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_freeze_support(x: int) -> int:
    return multiprocessing.freeze_support(x)


if __name__ == "__main__":
    pass
