"""Test difflib.diff_bytes L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import difflib  # noqa: F401


#@ requires True
#@ ensures True
def use_diff_bytes(x: int) -> int:
    return difflib.diff_bytes(x)


if __name__ == "__main__":
    pass
