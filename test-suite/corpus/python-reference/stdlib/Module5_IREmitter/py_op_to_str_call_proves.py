"""Test Module5_IREmitter.py_op_to_str L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module5_IREmitter  # noqa: F401


#@ requires True
#@ ensures True
def use_py_op_to_str(x: int) -> int:
    return Module5_IREmitter.py_op_to_str(x)


if __name__ == "__main__":
    pass
