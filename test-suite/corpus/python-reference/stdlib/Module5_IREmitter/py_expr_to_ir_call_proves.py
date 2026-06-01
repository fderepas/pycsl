"""Test Module5_IREmitter.py_expr_to_ir L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module5_IREmitter  # noqa: F401


#@ requires True
#@ ensures True
def use_py_expr_to_ir(x: int) -> int:
    return Module5_IREmitter.py_expr_to_ir(x)


if __name__ == "__main__":
    pass
