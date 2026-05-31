"""Test gzip.decompress L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gzip  # noqa: F401


#@ requires True
#@ ensures True
def use_decompress(x: int) -> int:
    return gzip.decompress(x)


if __name__ == "__main__":
    pass
