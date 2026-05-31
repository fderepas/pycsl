"""Test argparse.parse_args L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import argparse  # noqa: F401


#@ requires True
#@ ensures True
def use_parse_args(x: int) -> int:
    return argparse.parse_args(x)


if __name__ == "__main__":
    pass
