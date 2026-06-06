"""Test pathlib.chmod L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_chmod(x: int) -> int:
    return pathlib.chmod(x)


if __name__ == "__main__":
    pass
