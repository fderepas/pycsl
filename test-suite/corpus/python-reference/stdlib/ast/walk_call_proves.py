"""Test ast.walk L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ast  # noqa: F401


#@ requires True
#@ ensures True
def use_walk(x: int) -> int:
    return ast.walk(x)


if __name__ == "__main__":
    pass
