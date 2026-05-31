"""Test keyword.iskeyword L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import keyword  # noqa: F401


#@ requires True
#@ ensures True
def use_iskeyword(x: int) -> int:
    return keyword.iskeyword(x)


if __name__ == "__main__":
    pass
