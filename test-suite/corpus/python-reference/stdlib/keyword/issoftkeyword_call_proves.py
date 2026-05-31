"""Test keyword.issoftkeyword L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import keyword  # noqa: F401


#@ requires True
#@ ensures True
def use_issoftkeyword(x: int) -> int:
    return keyword.issoftkeyword(x)


if __name__ == "__main__":
    pass
