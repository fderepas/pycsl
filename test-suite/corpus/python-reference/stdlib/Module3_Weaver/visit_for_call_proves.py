"""Test Module3_Weaver.visit_for L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module3_Weaver  # noqa: F401


#@ requires True
#@ ensures True
def use_visit_for(x: int) -> int:
    return Module3_Weaver.visit_for(x)


if __name__ == "__main__":
    pass
