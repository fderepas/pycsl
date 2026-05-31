"""Test enum.bin L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import enum  # noqa: F401


#@ requires True
#@ ensures True
def use_bin(x: int) -> int:
    return enum.bin(x)


if __name__ == "__main__":
    pass
