"""Test faulthandler.enable L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import faulthandler  # noqa: F401


#@ requires True
#@ ensures True
def use_enable(x: int) -> int:
    return faulthandler.enable(x)


if __name__ == "__main__":
    pass
