"""Test multiprocessing.mp_semaphore L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_mp_semaphore(x: int) -> int:
    return multiprocessing.mp_semaphore(x)


if __name__ == "__main__":
    pass
