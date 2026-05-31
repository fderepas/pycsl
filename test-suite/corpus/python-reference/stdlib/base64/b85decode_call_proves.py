"""Test base64.b85decode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import base64  # noqa: F401


#@ requires True
#@ ensures True
def use_b85decode(x: int) -> int:
    return base64.b85decode(x)


if __name__ == "__main__":
    pass
