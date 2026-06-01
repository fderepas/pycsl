"""Test Module6_WhyMLTranspiler.uses_for L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module6_WhyMLTranspiler  # noqa: F401


#@ requires True
#@ ensures True
def use_uses_for(x: int) -> int:
    return Module6_WhyMLTranspiler.uses_for(x)


if __name__ == "__main__":
    pass
