"""Test Module2_Parser.CSLDiverges L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module2_Parser  # noqa: F401


#@ requires True
#@ ensures True
def use_CSLDiverges(x: int) -> int:
    return Module2_Parser.CSLDiverges(x)


if __name__ == "__main__":
    pass
