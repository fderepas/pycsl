"""Test Module5_IREmitter.process_for L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module5_IREmitter  # noqa: F401


#@ requires True
#@ ensures True
def use_process_for(x: int) -> int:
    return Module5_IREmitter.process_for(x)


if __name__ == "__main__":
    pass
