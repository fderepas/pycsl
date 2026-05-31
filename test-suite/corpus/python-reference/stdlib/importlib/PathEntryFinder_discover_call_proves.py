"""Test importlib.PathEntryFinder_discover L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_PathEntryFinder_discover(x: int) -> int:
    return importlib.PathEntryFinder_discover(x)


if __name__ == "__main__":
    pass
