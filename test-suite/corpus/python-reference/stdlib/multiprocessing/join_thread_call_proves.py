"""Test multiprocessing.join_thread L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_join_thread(x: int) -> int:
    return multiprocessing.join_thread(x)


if __name__ == "__main__":
    pass
