"""Test multiprocessing.starmap L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ requires True
#@ ensures True
def use_starmap(x: int) -> int:
    return multiprocessing.starmap(x)


if __name__ == "__main__":
    pass
