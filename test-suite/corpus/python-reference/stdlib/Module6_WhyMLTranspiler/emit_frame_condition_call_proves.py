"""Test Module6_WhyMLTranspiler.emit_frame_condition L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module6_WhyMLTranspiler  # noqa: F401


#@ requires True
#@ ensures True
def use_emit_frame_condition(x: int) -> int:
    return Module6_WhyMLTranspiler.emit_frame_condition(x)


if __name__ == "__main__":
    pass
