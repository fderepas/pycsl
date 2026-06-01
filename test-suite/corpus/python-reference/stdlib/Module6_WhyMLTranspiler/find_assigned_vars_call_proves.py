"""Test Module6_WhyMLTranspiler.find_assigned_vars L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module6_WhyMLTranspiler  # noqa: F401


#@ requires True
#@ ensures True
def use_find_assigned_vars(x: int) -> int:
    return Module6_WhyMLTranspiler.find_assigned_vars(x)


if __name__ == "__main__":
    pass
