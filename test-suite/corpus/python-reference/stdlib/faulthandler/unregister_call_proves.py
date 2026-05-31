"""Test faulthandler.unregister L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import faulthandler  # noqa: F401


#@ requires True
#@ ensures True
def use_unregister(x: int) -> int:
    return faulthandler.unregister(x)


if __name__ == "__main__":
    pass
