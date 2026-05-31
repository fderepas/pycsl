"""Test ast.literal_eval L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ast  # noqa: F401


#@ requires True
#@ ensures True
def use_literal_eval(x: int) -> int:
    return ast.literal_eval(x)


if __name__ == "__main__":
    pass
