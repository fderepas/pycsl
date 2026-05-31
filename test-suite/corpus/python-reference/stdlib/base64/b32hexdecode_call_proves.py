"""Test base64.b32hexdecode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import base64  # noqa: F401


#@ requires True
#@ ensures True
def use_b32hexdecode(x: int) -> int:
    return base64.b32hexdecode(x)


if __name__ == "__main__":
    pass
