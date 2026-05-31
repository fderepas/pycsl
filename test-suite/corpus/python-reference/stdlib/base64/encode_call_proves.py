"""Test base64.encode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import base64  # noqa: F401


#@ requires True
#@ ensures True
def use_encode(x: int) -> int:
    return base64.encode(x)


if __name__ == "__main__":
    pass
