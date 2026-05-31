"""Test token.ISEOF L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import token  # noqa: F401


#@ requires True
#@ ensures True
def use_ISEOF(x: int) -> int:
    return token.ISEOF(x)


if __name__ == "__main__":
    pass
