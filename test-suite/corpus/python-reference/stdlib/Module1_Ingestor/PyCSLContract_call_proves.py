"""Test Module1_Ingestor.PyCSLContract L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module1_Ingestor  # noqa: F401


#@ requires True
#@ ensures True
def use_PyCSLContract(x: int) -> int:
    return Module1_Ingestor.PyCSLContract(x)


if __name__ == "__main__":
    pass
