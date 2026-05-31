"""Test fnmatch.fnmatch L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import fnmatch  # noqa: F401


#@ requires True
#@ ensures True
def use_fnmatch(x: int) -> int:
    return fnmatch.fnmatch(x)


if __name__ == "__main__":
    pass
