"""Test multiprocessing.mp_pipe L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_mp_pipe(x: int) -> int:
    return multiprocessing.mp_pipe(x)


if __name__ == "__main__":
    pass
