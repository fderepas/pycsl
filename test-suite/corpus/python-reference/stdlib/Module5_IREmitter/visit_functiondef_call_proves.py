"""Test Module5_IREmitter.visit_functiondef L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module5_IREmitter  # noqa: F401


#@ requires True
#@ ensures True
def use_visit_functiondef(x: int) -> int:
    return Module5_IREmitter.visit_functiondef(x)


if __name__ == "__main__":
    pass
