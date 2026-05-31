"""Test ast.iter_child_nodes L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ast  # noqa: F401


#@ requires True
#@ ensures True
def use_iter_child_nodes(x: int) -> int:
    return ast.iter_child_nodes(x)


if __name__ == "__main__":
    pass
