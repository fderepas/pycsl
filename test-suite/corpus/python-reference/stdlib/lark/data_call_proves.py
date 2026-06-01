"""Test lark.data L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import lark  # noqa: F401


#@ requires True
#@ ensures True
def use_data(x: int) -> int:
    return lark.data(x)


if __name__ == "__main__":
    pass
