"""Test importlib.SourceLoader_set_data L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_SourceLoader_set_data(x: int) -> int:
    return importlib.SourceLoader_set_data(x)


if __name__ == "__main__":
    pass
