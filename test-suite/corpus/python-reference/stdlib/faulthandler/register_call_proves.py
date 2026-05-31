"""Test faulthandler.register L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import faulthandler  # noqa: F401


#@ requires True
#@ ensures True
def use_register(x: int) -> int:
    return faulthandler.register(x)


if __name__ == "__main__":
    pass
