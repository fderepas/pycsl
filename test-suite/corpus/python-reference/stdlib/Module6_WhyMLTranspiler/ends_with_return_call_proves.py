"""Test Module6_WhyMLTranspiler.ends_with_return L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module6_WhyMLTranspiler  # noqa: F401


#@ requires True
#@ ensures True
def use_ends_with_return(x: int) -> int:
    return Module6_WhyMLTranspiler.ends_with_return(x)


if __name__ == "__main__":
    pass
