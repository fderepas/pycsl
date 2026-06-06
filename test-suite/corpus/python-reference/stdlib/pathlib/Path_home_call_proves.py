"""Test pathlib.Path_home L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_Path_home(x: int) -> int:
    return pathlib.Path_home(x)


if __name__ == "__main__":
    pass
