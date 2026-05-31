"""Test ast.get_docstring L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ast  # noqa: F401


#@ requires True
#@ ensures True
def use_get_docstring(x: int) -> int:
    return ast.get_docstring(x)


if __name__ == "__main__":
    pass
