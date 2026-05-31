"""Test difflib.get_close_matches L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import difflib  # noqa: F401


#@ requires True
#@ ensures True
def use_get_close_matches(x: int) -> int:
    return difflib.get_close_matches(x)


if __name__ == "__main__":
    pass
