"""Test multiprocessing.mp_listener L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_mp_listener(x: int) -> int:
    return multiprocessing.mp_listener(x)


if __name__ == "__main__":
    pass
