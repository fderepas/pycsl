"""Test gzip.compress L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gzip  # noqa: F401


#@ requires True
#@ ensures True
def use_compress(x: int) -> int:
    return gzip.compress(x)


if __name__ == "__main__":
    pass
