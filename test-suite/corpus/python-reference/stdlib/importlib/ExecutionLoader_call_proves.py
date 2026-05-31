"""Test importlib.ExecutionLoader L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_ExecutionLoader(x: int) -> int:
    return importlib.ExecutionLoader(x)


if __name__ == "__main__":
    pass
