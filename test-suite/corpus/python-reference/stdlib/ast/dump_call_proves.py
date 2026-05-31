"""Test ast.dump L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ast  # noqa: F401


#@ requires True
#@ ensures True
def use_dump(x: int) -> int:
    return ast.dump(x)


if __name__ == "__main__":
    pass
