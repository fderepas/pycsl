"""Test difflib.restore L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import difflib  # noqa: F401


#@ requires True
#@ ensures True
def use_restore(x: int) -> int:
    return difflib.restore(x)


if __name__ == "__main__":
    pass
