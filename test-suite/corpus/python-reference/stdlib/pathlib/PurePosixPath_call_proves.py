"""Test pathlib.PurePosixPath L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_PurePosixPath(x: int) -> int:
    return pathlib.PurePosixPath(x)


if __name__ == "__main__":
    pass
