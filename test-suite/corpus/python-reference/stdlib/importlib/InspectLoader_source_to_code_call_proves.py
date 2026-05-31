"""Test importlib.InspectLoader_source_to_code L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_InspectLoader_source_to_code(x: int) -> int:
    return importlib.InspectLoader_source_to_code(x)


if __name__ == "__main__":
    pass
