"""Test doctest.debug_src L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import doctest  # noqa: F401


#@ requires True
#@ ensures True
def use_debug_src(x: int) -> int:
    return doctest.debug_src(x)


if __name__ == "__main__":
    pass
