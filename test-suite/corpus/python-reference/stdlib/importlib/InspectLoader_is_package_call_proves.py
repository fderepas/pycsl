"""Test importlib.InspectLoader_is_package L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_InspectLoader_is_package(x: int) -> int:
    return importlib.InspectLoader_is_package(x)


if __name__ == "__main__":
    pass
