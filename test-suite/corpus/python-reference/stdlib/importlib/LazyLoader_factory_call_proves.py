"""Test importlib.LazyLoader_factory L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_LazyLoader_factory(x: int) -> int:
    return importlib.LazyLoader_factory(x)


if __name__ == "__main__":
    pass
