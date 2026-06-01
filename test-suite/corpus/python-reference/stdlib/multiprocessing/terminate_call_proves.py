"""Test multiprocessing.terminate L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_terminate(x: int) -> int:
    return multiprocessing.terminate(x)


if __name__ == "__main__":
    pass
