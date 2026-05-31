"""Test doctest.set_unittest_reportflags L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import doctest  # noqa: F401


#@ requires True
#@ ensures True
def use_set_unittest_reportflags(x: int) -> int:
    return doctest.set_unittest_reportflags(x)


if __name__ == "__main__":
    pass
