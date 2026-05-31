"""Test fnmatch.filter L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import fnmatch  # noqa: F401


#@ requires True
#@ ensures True
def use_filter(x: int) -> int:
    return fnmatch.filter(x)


if __name__ == "__main__":
    pass
