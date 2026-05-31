"""Test importlib.SourceFileLoader_path_stats L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_SourceFileLoader_path_stats(x: int) -> int:
    return importlib.SourceFileLoader_path_stats(x)


if __name__ == "__main__":
    pass
