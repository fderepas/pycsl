"""Test bdb.set_trace L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import bdb  # noqa: F401


#@ requires True
#@ ensures True
def use_set_trace(x: int) -> int:
    return bdb.set_trace(x)


if __name__ == "__main__":
    pass
