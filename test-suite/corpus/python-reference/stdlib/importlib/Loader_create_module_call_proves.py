"""Test importlib.Loader_create_module L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_Loader_create_module(x: int) -> int:
    return importlib.Loader_create_module(x)


if __name__ == "__main__":
    pass
