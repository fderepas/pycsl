"""Test multiprocessing.get_start_method L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_get_start_method(x: int) -> int:
    return multiprocessing.get_start_method(x)


if __name__ == "__main__":
    pass
