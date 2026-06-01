"""Test Module2_Parser.PyCSLTransformer_field_access L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module2_Parser  # noqa: F401


#@ requires True
#@ ensures True
def use_PyCSLTransformer_field_access(x: int) -> int:
    return Module2_Parser.PyCSLTransformer_field_access(x)


if __name__ == "__main__":
    pass
