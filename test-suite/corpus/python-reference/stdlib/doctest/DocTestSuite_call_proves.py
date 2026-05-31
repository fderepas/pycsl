"""Test doctest.DocTestSuite L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import doctest  # noqa: F401


#@ requires True
#@ ensures True
def use_DocTestSuite(x: int) -> int:
    return doctest.DocTestSuite(x)


if __name__ == "__main__":
    pass
