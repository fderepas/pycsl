"""Test lark.UnexpectedToken L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import lark  # noqa: F401


#@ requires True
#@ ensures True
def use_UnexpectedToken(x: int) -> int:
    return lark.UnexpectedToken(x)


if __name__ == "__main__":
    pass
