"""Test libcst.matchers_matches L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import libcst  # noqa: F401


#@ requires True
#@ ensures True
def use_matchers_matches(x: int) -> int:
    return libcst.matchers_matches(x)


if __name__ == "__main__":
    pass
