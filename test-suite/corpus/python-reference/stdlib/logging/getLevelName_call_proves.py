"""Test logging.getLevelName L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import logging  # noqa: F401


#@ requires True
#@ ensures True
def use_getLevelName(x: int) -> int:
    return logging.getLevelName(x)


if __name__ == "__main__":
    pass
