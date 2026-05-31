"""Test difflib.context_diff L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import difflib  # noqa: F401


#@ requires True
#@ ensures True
def use_context_diff(x: int) -> int:
    return difflib.context_diff(x)


if __name__ == "__main__":
    pass
