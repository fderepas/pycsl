"""Test pathlib.mkdir L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_mkdir(x: int) -> int:
    return pathlib.mkdir(x)


if __name__ == "__main__":
    pass
