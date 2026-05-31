"""Test argparse.add_argument_group L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import argparse  # noqa: F401


#@ requires True
#@ ensures True
def use_add_argument_group(x: int) -> int:
    return argparse.add_argument_group(x)


if __name__ == "__main__":
    pass
