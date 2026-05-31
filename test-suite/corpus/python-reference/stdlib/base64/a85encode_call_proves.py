"""Test base64.a85encode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import base64  # noqa: F401


#@ requires True
#@ ensures True
def use_a85encode(x: int) -> int:
    return base64.a85encode(x)


if __name__ == "__main__":
    pass
