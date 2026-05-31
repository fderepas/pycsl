"""Test dis.findlinestarts L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import dis  # noqa: F401


#@ requires True
#@ ensures True
def use_findlinestarts(x: int) -> int:
    return dis.findlinestarts(x)


if __name__ == "__main__":
    pass
