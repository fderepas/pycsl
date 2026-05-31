"""Test copy.replace L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import copy  # noqa: F401


#@ requires True
#@ ensures True
def use_replace(x: int) -> int:
    return copy.replace(x)


if __name__ == "__main__":
    pass
