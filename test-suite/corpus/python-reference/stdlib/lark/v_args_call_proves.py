"""Test lark.v_args L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import lark  # noqa: F401


#@ requires True
#@ ensures True
def use_v_args(x: int) -> int:
    return lark.v_args(x)


if __name__ == "__main__":
    pass
