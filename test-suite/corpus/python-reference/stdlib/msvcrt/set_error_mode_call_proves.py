"""Test msvcrt.set_error_mode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import msvcrt  # noqa: F401


#@ requires True
#@ ensures True
def use_set_error_mode(x: int) -> int:
    return msvcrt.set_error_mode(x)


if __name__ == "__main__":
    pass
