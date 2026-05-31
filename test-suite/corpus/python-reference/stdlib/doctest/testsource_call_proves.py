"""Test doctest.testsource L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import doctest  # noqa: F401


#@ requires True
#@ ensures True
def use_testsource(x: int) -> int:
    return doctest.testsource(x)


if __name__ == "__main__":
    pass
