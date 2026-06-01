"""Test Module4_SemanticAnalyzer.contains_result L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module4_SemanticAnalyzer  # noqa: F401


#@ requires True
#@ ensures True
def use_contains_result(x: int) -> int:
    return Module4_SemanticAnalyzer.contains_result(x)


if __name__ == "__main__":
    pass
