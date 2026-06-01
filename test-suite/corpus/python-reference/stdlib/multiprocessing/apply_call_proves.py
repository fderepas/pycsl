"""Test multiprocessing.apply L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_apply(x: int) -> int:
    return multiprocessing.apply(x)


if __name__ == "__main__":
    pass
