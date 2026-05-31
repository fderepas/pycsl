"""Test importlib.import_module L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_import_module(x: int) -> int:
    return importlib.import_module(x)


if __name__ == "__main__":
    pass
