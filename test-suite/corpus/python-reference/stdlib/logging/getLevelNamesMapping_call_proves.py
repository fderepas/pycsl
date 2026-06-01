"""Test logging.getLevelNamesMapping L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import logging  # noqa: F401


#@ requires True
#@ ensures True
def use_getLevelNamesMapping(x: int) -> int:
    return logging.getLevelNamesMapping(x)


if __name__ == "__main__":
    pass
