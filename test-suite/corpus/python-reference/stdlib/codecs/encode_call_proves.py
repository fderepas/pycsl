"""Test codecs.encode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import codecs  # noqa: F401


#@ requires True
#@ ensures True
# (#44) `base64.encode` / `codecs.encode` return BYTES, which the model carries
# as `array int`. The driver declared `-> int` and returned the call into it,
# which is an L3-tc rejection once the emitter stops losing the `array` type.
def use_encode(x: int) -> list:
    return codecs.encode(x)


if __name__ == "__main__":
    pass
