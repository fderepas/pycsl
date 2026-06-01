"""Test msvcrt.ungetch L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import msvcrt  # noqa: F401


#@ requires True
#@ ensures True
def use_ungetch(x: int) -> int:
    return msvcrt.ungetch(x)


if __name__ == "__main__":
    pass
