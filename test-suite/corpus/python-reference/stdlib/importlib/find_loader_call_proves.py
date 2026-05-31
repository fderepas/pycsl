"""Test importlib.find_loader L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_find_loader(x: int) -> int:
    return importlib.find_loader(x)


if __name__ == "__main__":
    pass
