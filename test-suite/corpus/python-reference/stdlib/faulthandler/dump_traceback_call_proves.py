"""Test faulthandler.dump_traceback L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import faulthandler  # noqa: F401


#@ requires True
#@ ensures True
def use_dump_traceback(x: int) -> int:
    return faulthandler.dump_traceback(x)


if __name__ == "__main__":
    pass
