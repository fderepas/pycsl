"""Test argparse.add_mutually_exclusive_group L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import argparse  # noqa: F401


#@ requires True
#@ ensures True
def use_add_mutually_exclusive_group(x: int) -> int:
    return argparse.add_mutually_exclusive_group(x)


if __name__ == "__main__":
    pass
