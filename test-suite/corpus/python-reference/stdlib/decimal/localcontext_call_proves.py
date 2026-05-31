"""Test decimal.localcontext L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import decimal  # noqa: F401


#@ requires True
#@ ensures True
def use_localcontext(x: int) -> int:
    return decimal.localcontext(x)


if __name__ == "__main__":
    pass
