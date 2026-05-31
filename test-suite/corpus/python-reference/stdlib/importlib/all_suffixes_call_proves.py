"""Test importlib.all_suffixes L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_all_suffixes(x: int) -> int:
    return importlib.all_suffixes(x)


if __name__ == "__main__":
    pass
