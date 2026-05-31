"""Test token.ISNONTERMINAL L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import token  # noqa: F401


#@ requires True
#@ ensures True
def use_ISNONTERMINAL(x: int) -> int:
    return token.ISNONTERMINAL(x)


if __name__ == "__main__":
    pass
