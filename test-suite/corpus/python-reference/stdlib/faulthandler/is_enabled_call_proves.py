"""Test faulthandler.is_enabled L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import faulthandler  # noqa: F401


#@ requires True
#@ ensures True
def use_is_enabled(x: int) -> int:
    return faulthandler.is_enabled(x)


if __name__ == "__main__":
    pass
