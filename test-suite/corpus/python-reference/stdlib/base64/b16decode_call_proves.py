"""Test base64.b16decode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import base64  # noqa: F401


#@ requires True
#@ ensures True
def use_b16decode(x: int) -> int:
    return base64.b16decode(x)


if __name__ == "__main__":
    pass
