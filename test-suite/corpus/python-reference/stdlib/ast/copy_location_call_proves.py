"""Test ast.copy_location L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ast  # noqa: F401


#@ requires True
#@ ensures True
def use_copy_location(x: int) -> int:
    return ast.copy_location(x)


if __name__ == "__main__":
    pass
