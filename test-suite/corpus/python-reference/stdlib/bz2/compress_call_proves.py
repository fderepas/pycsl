"""Test bz2.compress L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import bz2  # noqa: F401


#@ requires True
#@ ensures True
def use_compress(x: int) -> int:
    return bz2.compress(x)


if __name__ == "__main__":
    pass
