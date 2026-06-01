"""Test multiprocessing.mp_lock L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_mp_lock(x: int) -> int:
    return multiprocessing.mp_lock(x)


if __name__ == "__main__":
    pass
