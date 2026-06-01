"""Test multiprocessing.mp_client L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_mp_client(x: int) -> int:
    return multiprocessing.mp_client(x)


if __name__ == "__main__":
    pass
