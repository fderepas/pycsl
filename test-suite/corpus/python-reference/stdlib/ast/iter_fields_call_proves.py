"""Test ast.iter_fields L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ast  # noqa: F401


#@ requires True
#@ ensures True
def use_iter_fields(x: int) -> int:
    return ast.iter_fields(x)


if __name__ == "__main__":
    pass
