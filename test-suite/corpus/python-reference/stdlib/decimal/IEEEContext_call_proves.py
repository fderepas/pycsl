"""Test decimal.IEEEContext L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import decimal  # noqa: F401


#@ requires True
#@ ensures True
def use_IEEEContext(x: int) -> int:
    return decimal.IEEEContext(x)


if __name__ == "__main__":
    pass
