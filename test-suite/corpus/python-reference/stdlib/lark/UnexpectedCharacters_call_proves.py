"""Test lark.UnexpectedCharacters L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import lark  # noqa: F401


#@ requires True
#@ ensures True
def use_UnexpectedCharacters(x: int) -> int:
    return lark.UnexpectedCharacters(x)


if __name__ == "__main__":
    pass
