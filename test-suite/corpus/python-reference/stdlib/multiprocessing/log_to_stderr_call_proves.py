"""Test multiprocessing.log_to_stderr L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_log_to_stderr(x: int) -> int:
    return multiprocessing.log_to_stderr(x)


if __name__ == "__main__":
    pass
