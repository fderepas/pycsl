"""Test getpass.getpass L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import getpass  # noqa: F401


#@ requires True
#@ ensures True
def use_getpass(x: int) -> int:
    return getpass.getpass(x)


if __name__ == "__main__":
    pass
