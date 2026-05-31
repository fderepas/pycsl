"""Test code.interact L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import code  # noqa: F401


#@ requires True
#@ ensures True
def use_interact(x: int) -> int:
    return code.interact(x)


if __name__ == "__main__":
    pass
