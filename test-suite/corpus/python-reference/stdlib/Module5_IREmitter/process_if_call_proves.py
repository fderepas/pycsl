"""Test Module5_IREmitter.process_if L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module5_IREmitter  # noqa: F401


#@ requires True
#@ ensures True
def use_process_if(x: int) -> int:
    return Module5_IREmitter.process_if(x)


if __name__ == "__main__":
    pass
