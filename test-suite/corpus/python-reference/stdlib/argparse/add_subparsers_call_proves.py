"""Test argparse.add_subparsers L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import argparse  # noqa: F401


#@ requires True
#@ ensures True
def use_add_subparsers(x: int) -> int:
    return argparse.add_subparsers(x)


if __name__ == "__main__":
    pass
