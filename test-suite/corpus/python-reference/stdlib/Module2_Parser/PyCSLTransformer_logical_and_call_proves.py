"""Test Module2_Parser.PyCSLTransformer_logical_and L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module2_Parser  # noqa: F401


#@ requires True
#@ ensures True
def use_PyCSLTransformer_logical_and(x: int) -> int:
    return Module2_Parser.PyCSLTransformer_logical_and(x)


if __name__ == "__main__":
    pass
