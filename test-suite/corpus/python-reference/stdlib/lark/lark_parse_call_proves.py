"""Test lark.lark_parse L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import lark  # noqa: F401


#@ requires True
#@ ensures True
def use_lark_parse(x: int) -> int:
    return lark.lark_parse(x)


if __name__ == "__main__":
    pass
