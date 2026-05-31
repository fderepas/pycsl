"""Test importlib.cache_from_source L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_cache_from_source(x: int) -> int:
    return importlib.cache_from_source(x)


if __name__ == "__main__":
    pass
