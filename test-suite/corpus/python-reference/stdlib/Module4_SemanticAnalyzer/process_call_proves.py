"""Test Module4_SemanticAnalyzer.process L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module4_SemanticAnalyzer  # noqa: F401


#@ requires True
#@ ensures True
def use_process(x: int) -> int:
    return Module4_SemanticAnalyzer.process(x)


if __name__ == "__main__":
    pass
