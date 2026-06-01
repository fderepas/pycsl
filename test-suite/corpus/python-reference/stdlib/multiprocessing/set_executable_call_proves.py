"""Test multiprocessing.set_executable L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_set_executable(x: int) -> int:
    return multiprocessing.set_executable(x)


if __name__ == "__main__":
    pass
