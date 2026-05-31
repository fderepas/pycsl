"""Test binascii.b2a_uu L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import binascii  # noqa: F401


#@ requires True
#@ ensures True
def use_b2a_uu(x: int) -> int:
    return binascii.b2a_uu(x)


if __name__ == "__main__":
    pass
