"""Test logging.info L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import logging  # noqa: F401


#@ requires True
#@ ensures True
def use_info(x: int) -> int:
    return logging.info(x)


if __name__ == "__main__":
    pass
