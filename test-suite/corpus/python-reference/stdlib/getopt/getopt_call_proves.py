"""Test getopt.getopt L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import getopt  # noqa: F401


#@ requires True
#@ ensures True
def use_getopt(x: int) -> int:
    return getopt.getopt(x)


if __name__ == "__main__":
    pass
