"""Test faulthandler.cancel_dump_traceback_later L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import faulthandler  # noqa: F401


#@ requires True
#@ ensures True
def use_cancel_dump_traceback_later(x: int) -> int:
    return faulthandler.cancel_dump_traceback_later(x)


if __name__ == "__main__":
    pass
