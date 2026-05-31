"""Test argparse.get_default L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import argparse  # noqa: F401


#@ requires True
#@ ensures True
def use_get_default(x: int) -> int:
    return argparse.get_default(x)


if __name__ == "__main__":
    pass
