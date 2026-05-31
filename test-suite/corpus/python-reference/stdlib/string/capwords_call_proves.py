"""Test string.capwords L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import string  # noqa: F401


#@ requires True
#@ ensures True
def use_capwords(x: int) -> int:
    return string.capwords(x)


if __name__ == "__main__":
    pass
