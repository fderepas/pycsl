"""Test difflib.IS_LINE_JUNK L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import difflib  # noqa: F401


#@ requires True
#@ ensures True
def use_IS_LINE_JUNK(x: int) -> int:
    return difflib.IS_LINE_JUNK(x)


if __name__ == "__main__":
    pass
