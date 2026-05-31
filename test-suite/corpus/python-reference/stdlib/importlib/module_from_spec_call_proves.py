"""Test importlib.module_from_spec L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_module_from_spec(x: int) -> int:
    return importlib.module_from_spec(x)


if __name__ == "__main__":
    pass
