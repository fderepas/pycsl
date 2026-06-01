"""Test multiprocessing.current_process L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_current_process(x: int) -> int:
    return multiprocessing.current_process(x)


if __name__ == "__main__":
    pass
