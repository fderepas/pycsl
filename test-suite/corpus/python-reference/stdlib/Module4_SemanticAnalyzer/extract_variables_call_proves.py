"""Test Module4_SemanticAnalyzer.extract_variables L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module4_SemanticAnalyzer  # noqa: F401


#@ requires True
#@ ensures True
def use_extract_variables(x: int) -> int:
    return Module4_SemanticAnalyzer.extract_variables(x)


if __name__ == "__main__":
    pass
