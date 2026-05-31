"""Test binascii.b2a_hex L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import binascii  # noqa: F401


#@ requires True
#@ ensures True
def use_b2a_hex(x: int) -> int:
    return binascii.b2a_hex(x)


if __name__ == "__main__":
    pass
