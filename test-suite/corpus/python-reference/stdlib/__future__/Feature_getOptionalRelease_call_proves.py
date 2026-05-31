"""Test __future__.Feature_getOptionalRelease L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import __future__  # noqa: F401


#@ requires True
#@ ensures True
def use_Feature_getOptionalRelease(x: int) -> int:
    return __future__.Feature_getOptionalRelease(x)


if __name__ == "__main__":
    pass
