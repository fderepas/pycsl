"""Test importlib.SourceLoader_get_source L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_SourceLoader_get_source(x: int) -> int:
    return importlib.SourceLoader_get_source(x)


if __name__ == "__main__":
    pass
