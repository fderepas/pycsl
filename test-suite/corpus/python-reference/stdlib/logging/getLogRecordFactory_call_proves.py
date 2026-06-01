"""Test logging.getLogRecordFactory L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import logging  # noqa: F401


#@ requires True
#@ ensures True
def use_getLogRecordFactory(x: int) -> int:
    return logging.getLogRecordFactory(x)


if __name__ == "__main__":
    pass
