"""Test msvcrt.getche L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import msvcrt  # noqa: F401


#@ requires True
#@ ensures True
def use_getche(x: int) -> int:
    return msvcrt.getche(x)


if __name__ == "__main__":
    pass
