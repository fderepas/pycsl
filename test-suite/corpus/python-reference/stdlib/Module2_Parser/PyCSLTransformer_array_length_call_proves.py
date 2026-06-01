"""Test Module2_Parser.PyCSLTransformer_array_length L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module2_Parser  # noqa: F401


#@ requires True
#@ ensures True
def use_PyCSLTransformer_array_length(x: int) -> int:
    return Module2_Parser.PyCSLTransformer_array_length(x)


if __name__ == "__main__":
    pass
