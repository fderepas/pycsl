"""Test Module2_Parser.BinOp L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module2_Parser  # noqa: F401


#@ requires True
#@ ensures True
def use_BinOp(x: int) -> int:
    return Module2_Parser.BinOp(x)


if __name__ == "__main__":
    pass
