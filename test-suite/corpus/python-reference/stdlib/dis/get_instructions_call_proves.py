"""Test dis.get_instructions L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import dis  # noqa: F401


#@ requires True
#@ ensures True
def use_get_instructions(x: int) -> int:
    return dis.get_instructions(x)


if __name__ == "__main__":
    pass
