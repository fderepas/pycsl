"""Test doctest.register_optionflag L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import doctest  # noqa: F401


#@ requires True
#@ ensures True
def use_register_optionflag(x: int) -> int:
    return doctest.register_optionflag(x)


if __name__ == "__main__":
    pass
