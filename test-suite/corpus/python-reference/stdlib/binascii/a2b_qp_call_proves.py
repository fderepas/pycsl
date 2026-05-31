"""Test binascii.a2b_qp L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import binascii  # noqa: F401


#@ requires True
#@ ensures True
def use_a2b_qp(x: int) -> int:
    return binascii.a2b_qp(x)


if __name__ == "__main__":
    pass
