"""Test pathlib.rmdir L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_rmdir(x: int) -> int:
    return pathlib.rmdir(x)


if __name__ == "__main__":
    pass
