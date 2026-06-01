"""Test logging.captureWarnings L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import logging  # noqa: F401


#@ requires True
#@ ensures True
def use_captureWarnings(x: int) -> int:
    return logging.captureWarnings(x)


if __name__ == "__main__":
    pass
