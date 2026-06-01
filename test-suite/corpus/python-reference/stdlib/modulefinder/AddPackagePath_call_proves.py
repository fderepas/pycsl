"""Test modulefinder.AddPackagePath L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import modulefinder  # noqa: F401


#@ requires True
#@ ensures True
def use_AddPackagePath(x: int) -> int:
    return modulefinder.AddPackagePath(x)


if __name__ == "__main__":
    pass
