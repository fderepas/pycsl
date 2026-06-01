"""Test Module2_Parser.PyCSLTransformer_forall_expr L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module2_Parser  # noqa: F401


#@ requires True
#@ ensures True
def use_PyCSLTransformer_forall_expr(x: int) -> int:
    return Module2_Parser.PyCSLTransformer_forall_expr(x)


if __name__ == "__main__":
    pass
