"""Test decimal.getcontext L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import decimal  # noqa: F401


#@ requires True
#@ ensures True
def use_getcontext(x: int) -> int:
    return decimal.getcontext(x)


if __name__ == "__main__":
    pass
