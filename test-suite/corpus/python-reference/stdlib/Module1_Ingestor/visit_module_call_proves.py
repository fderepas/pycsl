"""Test Module1_Ingestor.visit_module L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module1_Ingestor  # noqa: F401


#@ requires True
#@ ensures True
def use_visit_module(x: int) -> int:
    return Module1_Ingestor.visit_module(x)


if __name__ == "__main__":
    pass
