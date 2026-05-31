"""Test argparse.error_exit L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import argparse  # noqa: F401


#@ requires True
#@ ensures True
def use_error_exit(x: int) -> int:
    return argparse.error_exit(x)


if __name__ == "__main__":
    pass
