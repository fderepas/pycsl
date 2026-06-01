"""Test Module5_IREmitter.collect_2d_params L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module5_IREmitter  # noqa: F401


#@ requires True
#@ ensures True
def use_collect_2d_params(x: int) -> int:
    return Module5_IREmitter.collect_2d_params(x)


if __name__ == "__main__":
    pass
