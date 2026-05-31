"""Test importlib.PathFinder_find_spec L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_PathFinder_find_spec(x: int) -> int:
    return importlib.PathFinder_find_spec(x)


if __name__ == "__main__":
    pass
