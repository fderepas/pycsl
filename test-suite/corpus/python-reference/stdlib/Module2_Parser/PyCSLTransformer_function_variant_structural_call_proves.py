"""Test Module2_Parser.PyCSLTransformer_function_variant_structural L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module2_Parser  # noqa: F401


#@ requires True
#@ ensures True
def use_PyCSLTransformer_function_variant_structural(x: int) -> int:
    return Module2_Parser.PyCSLTransformer_function_variant_structural(x)


if __name__ == "__main__":
    pass
