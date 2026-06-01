"""Test Module2_Parser.CSLRequires L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module2_Parser  # noqa: F401


#@ requires True
#@ ensures True
def use_CSLRequires(x: int) -> int:
    return Module2_Parser.CSLRequires(x)


if __name__ == "__main__":
    pass
