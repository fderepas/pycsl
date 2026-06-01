"""Test Module2_Parser.PyCSLTransformer_equality L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module2_Parser  # noqa: F401


#@ requires True
#@ ensures True
def use_PyCSLTransformer_equality(x: int) -> int:
    return Module2_Parser.PyCSLTransformer_equality(x)


if __name__ == "__main__":
    pass
