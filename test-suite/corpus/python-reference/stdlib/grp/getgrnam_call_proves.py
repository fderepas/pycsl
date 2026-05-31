"""Test grp.getgrnam L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import grp  # noqa: F401


#@ requires True
#@ ensures True
def use_getgrnam(x: int) -> int:
    return grp.getgrnam(x)


if __name__ == "__main__":
    pass
