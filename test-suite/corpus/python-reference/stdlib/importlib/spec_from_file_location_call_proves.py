"""Test importlib.spec_from_file_location L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_spec_from_file_location(x: int) -> int:
    return importlib.spec_from_file_location(x)


if __name__ == "__main__":
    pass
