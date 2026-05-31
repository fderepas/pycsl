"""Test importlib.source_hash L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_source_hash(x: int) -> int:
    return importlib.source_hash(x)


if __name__ == "__main__":
    pass
