"""Test importlib.source_from_cache L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_source_from_cache(x: int) -> int:
    return importlib.source_from_cache(x)


if __name__ == "__main__":
    pass
