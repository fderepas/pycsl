"""Test doctest.DocFileSuite L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import doctest  # noqa: F401


#@ requires True
#@ ensures True
def use_DocFileSuite(x: int) -> int:
    return doctest.DocFileSuite(x)


if __name__ == "__main__":
    pass
