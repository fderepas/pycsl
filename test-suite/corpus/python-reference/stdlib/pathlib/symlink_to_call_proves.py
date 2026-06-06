"""Test pathlib.symlink_to L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_symlink_to(x: int) -> int:
    return pathlib.symlink_to(x)


if __name__ == "__main__":
    pass
