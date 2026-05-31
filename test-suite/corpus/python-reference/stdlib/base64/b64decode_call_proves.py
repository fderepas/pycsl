"""Test base64.b64decode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import base64  # noqa: F401


#@ requires True
#@ ensures True
def use_b64decode(x: int) -> int:
    return base64.b64decode(x)


if __name__ == "__main__":
    pass
