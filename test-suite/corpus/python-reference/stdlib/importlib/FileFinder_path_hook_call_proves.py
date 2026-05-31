"""Test importlib.FileFinder_path_hook L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_FileFinder_path_hook(x: int) -> int:
    return importlib.FileFinder_path_hook(x)


if __name__ == "__main__":
    pass
