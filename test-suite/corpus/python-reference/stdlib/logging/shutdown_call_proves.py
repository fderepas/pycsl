"""Test logging.shutdown L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import logging  # noqa: F401


#@ requires True
#@ ensures True
def use_shutdown(x: int) -> int:
    return logging.shutdown(x)


if __name__ == "__main__":
    pass
