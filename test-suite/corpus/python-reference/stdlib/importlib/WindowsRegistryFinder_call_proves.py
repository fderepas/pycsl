"""Test importlib.WindowsRegistryFinder L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_WindowsRegistryFinder(x: int) -> int:
    return importlib.WindowsRegistryFinder(x)


if __name__ == "__main__":
    pass
