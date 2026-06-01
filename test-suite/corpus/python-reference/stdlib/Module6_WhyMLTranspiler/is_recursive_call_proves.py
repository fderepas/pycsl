"""Test Module6_WhyMLTranspiler.is_recursive L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module6_WhyMLTranspiler  # noqa: F401


#@ requires True
#@ ensures True
def use_is_recursive(x: int) -> int:
    return Module6_WhyMLTranspiler.is_recursive(x)


if __name__ == "__main__":
    pass
