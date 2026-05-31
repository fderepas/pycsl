"""Test dis.stack_effect L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import dis  # noqa: F401


#@ requires True
#@ ensures True
def use_stack_effect(x: int) -> int:
    return dis.stack_effect(x)


if __name__ == "__main__":
    pass
