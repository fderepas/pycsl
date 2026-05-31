"""Test token.ISTERMINAL L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import token  # noqa: F401


#@ requires True
#@ ensures True
def use_ISTERMINAL(x: int) -> int:
    return token.ISTERMINAL(x)


if __name__ == "__main__":
    pass
