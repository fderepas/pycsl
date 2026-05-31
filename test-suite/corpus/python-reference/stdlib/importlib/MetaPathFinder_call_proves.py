"""Test importlib.MetaPathFinder L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_MetaPathFinder(x: int) -> int:
    return importlib.MetaPathFinder(x)


if __name__ == "__main__":
    pass
