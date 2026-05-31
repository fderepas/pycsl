"""Test ctypes.get_last_error L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import ctypes  # noqa: F401


#@ ensures True
def use_get_last_error_unsafe(x: int) -> int:
    return ctypes.get_last_error(x)


if __name__ == "__main__":
    pass
