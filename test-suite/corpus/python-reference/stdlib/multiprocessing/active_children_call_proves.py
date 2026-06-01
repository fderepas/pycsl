"""Test multiprocessing.active_children L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_active_children(x: int) -> int:
    return multiprocessing.active_children(x)


if __name__ == "__main__":
    pass
