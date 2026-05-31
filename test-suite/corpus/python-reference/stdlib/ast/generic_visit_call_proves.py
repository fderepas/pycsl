"""Test ast.generic_visit L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ast  # noqa: F401


#@ requires True
#@ ensures True
def use_generic_visit(x: int) -> int:
    return ast.generic_visit(x)


if __name__ == "__main__":
    pass
