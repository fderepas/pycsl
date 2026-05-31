"""Test argparse.ArgumentError L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import argparse  # noqa: F401


#@ requires True
#@ ensures True
def use_ArgumentError(x: int) -> int:
    return argparse.ArgumentError(x)


if __name__ == "__main__":
    pass
