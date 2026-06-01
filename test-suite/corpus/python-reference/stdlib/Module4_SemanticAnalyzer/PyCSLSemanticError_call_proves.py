"""Test Module4_SemanticAnalyzer.PyCSLSemanticError L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module4_SemanticAnalyzer  # noqa: F401


#@ requires True
#@ ensures True
def use_PyCSLSemanticError(x: int) -> int:
    return Module4_SemanticAnalyzer.PyCSLSemanticError(x)


if __name__ == "__main__":
    pass
