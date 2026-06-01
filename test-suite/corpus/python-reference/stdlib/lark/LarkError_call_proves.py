"""Test lark.LarkError L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import lark  # noqa: F401


#@ requires True
#@ ensures True
def use_LarkError(x: int) -> int:
    return lark.LarkError(x)


if __name__ == "__main__":
    pass
