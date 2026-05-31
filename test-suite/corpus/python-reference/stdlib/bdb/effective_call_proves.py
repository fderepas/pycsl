"""Test bdb.effective L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import bdb  # noqa: F401


#@ requires True
#@ ensures True
def use_effective(x: int) -> int:
    return bdb.effective(x)


if __name__ == "__main__":
    pass
