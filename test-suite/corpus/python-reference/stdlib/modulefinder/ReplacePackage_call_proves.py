"""Test modulefinder.ReplacePackage L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import modulefinder  # noqa: F401


#@ requires True
#@ ensures True
def use_ReplacePackage(x: int) -> int:
    return modulefinder.ReplacePackage(x)


if __name__ == "__main__":
    pass
