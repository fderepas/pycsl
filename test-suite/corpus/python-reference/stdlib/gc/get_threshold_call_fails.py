"""Test gc.get_threshold L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import gc  # noqa: F401


#@ ensures True
def use_get_threshold_unsafe(x: int) -> int:
    return gc.get_threshold(x)


if __name__ == "__main__":
    pass
