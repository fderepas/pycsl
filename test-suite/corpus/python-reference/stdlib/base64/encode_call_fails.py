"""Test base64.encode L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import base64  # noqa: F401


#@ ensures True
# (#44) `base64.encode` / `codecs.encode` return BYTES, which the model carries
# as `array int`. The driver declared `-> int` and returned the call into it,
# which is an L3-tc rejection once the emitter stops losing the `array` type.
def use_encode_unsafe(x: int) -> list:
    return base64.encode(x)


if __name__ == "__main__":
    pass
