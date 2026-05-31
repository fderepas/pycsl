"""Test binascii.crc32 L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import binascii  # noqa: F401


#@ requires True
#@ ensures True
def use_crc32(x: int) -> int:
    return binascii.crc32(x)


if __name__ == "__main__":
    pass
