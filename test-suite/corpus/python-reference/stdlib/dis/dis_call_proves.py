"""Test dis.dis L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import dis  # noqa: F401


#@ requires True
#@ ensures True
def use_dis(x: int) -> int:
    return dis.dis(x)


if __name__ == "__main__":
    pass
