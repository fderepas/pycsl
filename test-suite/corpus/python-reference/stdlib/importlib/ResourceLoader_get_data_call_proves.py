"""Test importlib.ResourceLoader_get_data L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_ResourceLoader_get_data(x: int) -> int:
    return importlib.ResourceLoader_get_data(x)


if __name__ == "__main__":
    pass
