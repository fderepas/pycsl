"""Test binascii.crc_hqx L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import binascii  # noqa: F401


#@ requires True
#@ ensures True
def use_crc_hqx(x: int) -> int:
    return binascii.crc_hqx(x)


if __name__ == "__main__":
    pass
