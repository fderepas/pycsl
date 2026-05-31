"""Test bz2.decompress L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import bz2  # noqa: F401


#@ requires True
#@ ensures True
def use_decompress(x: int) -> int:
    return bz2.decompress(x)


if __name__ == "__main__":
    pass
