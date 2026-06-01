"""Test Module3_Weaver.visit_while L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module3_Weaver  # noqa: F401


#@ requires True
#@ ensures True
def use_visit_while(x: int) -> int:
    return Module3_Weaver.visit_while(x)


if __name__ == "__main__":
    pass
