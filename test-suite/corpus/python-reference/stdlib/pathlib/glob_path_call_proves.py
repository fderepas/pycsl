"""Test pathlib.glob_path L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_glob_path(x: int) -> int:
    return pathlib.glob_path(x)


if __name__ == "__main__":
    pass
