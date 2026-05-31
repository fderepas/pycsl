"""Test ast.fix_missing_locations L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ast  # noqa: F401


#@ requires True
#@ ensures True
def use_fix_missing_locations(x: int) -> int:
    return ast.fix_missing_locations(x)


if __name__ == "__main__":
    pass
