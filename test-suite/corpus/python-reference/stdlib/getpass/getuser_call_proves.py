"""Test getpass.getuser L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import getpass  # noqa: F401


#@ requires True
#@ ensures True
def use_getuser(x: int) -> int:
    return getpass.getuser(x)


if __name__ == "__main__":
    pass
