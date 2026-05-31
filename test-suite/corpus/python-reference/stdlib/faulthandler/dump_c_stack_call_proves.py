"""Test faulthandler.dump_c_stack L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import faulthandler  # noqa: F401


#@ requires True
#@ ensures True
def use_dump_c_stack(x: int) -> int:
    return faulthandler.dump_c_stack(x)


if __name__ == "__main__":
    pass
