"""Test msvcrt.putch L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import msvcrt  # noqa: F401


#@ requires True
#@ ensures True
def use_putch(x: int) -> int:
    return msvcrt.putch(x)


if __name__ == "__main__":
    pass
