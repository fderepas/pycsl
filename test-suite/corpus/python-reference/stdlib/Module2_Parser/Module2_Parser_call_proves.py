"""Test Module2_Parser.Module2_Parser L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module2_Parser  # noqa: F401


#@ requires True
#@ ensures True
def use_Module2_Parser(x: int) -> int:
    return Module2_Parser.Module2_Parser(x)


if __name__ == "__main__":
    pass
