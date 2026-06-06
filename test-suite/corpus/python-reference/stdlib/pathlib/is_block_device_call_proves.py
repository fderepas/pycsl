"""Test pathlib.is_block_device L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_is_block_device(x: int) -> int:
    return pathlib.is_block_device(x)


if __name__ == "__main__":
    pass
