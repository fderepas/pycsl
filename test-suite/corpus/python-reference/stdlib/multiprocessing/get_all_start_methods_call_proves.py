"""Test multiprocessing.get_all_start_methods L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_get_all_start_methods(x: int) -> int:
    return multiprocessing.get_all_start_methods(x)


if __name__ == "__main__":
    pass
