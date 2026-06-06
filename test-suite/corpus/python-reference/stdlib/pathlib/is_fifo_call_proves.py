"""Test pathlib.is_fifo L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import pathlib  # noqa: F401


#@ requires True
#@ ensures True
def use_is_fifo(x: int) -> int:
    return pathlib.is_fifo(x)


if __name__ == "__main__":
    pass
