"""Test Module6_WhyMLTranspiler.expr_to_whyml L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module6_WhyMLTranspiler  # noqa: F401


#@ requires True
#@ ensures True
def use_expr_to_whyml(x: int) -> int:
    return Module6_WhyMLTranspiler.expr_to_whyml(x)


if __name__ == "__main__":
    pass
