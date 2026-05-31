"""Test copyreg.constructor L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import copyreg  # noqa: F401


#@ requires True
#@ ensures True
def use_constructor(x: int) -> int:
    return copyreg.constructor(x)


if __name__ == "__main__":
    pass
