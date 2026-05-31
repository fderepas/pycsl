"""Test importlib.SourceLoader_path_mtime L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import importlib  # noqa: F401


#@ requires True
#@ ensures True
def use_SourceLoader_path_mtime(x: int) -> int:
    return importlib.SourceLoader_path_mtime(x)


if __name__ == "__main__":
    pass
