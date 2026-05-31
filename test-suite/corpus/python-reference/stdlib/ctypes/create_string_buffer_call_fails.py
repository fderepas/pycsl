"""Test ctypes.create_string_buffer L5 — negative: caller can't discharge requires.

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
def use_create_string_buffer_unsafe(x: int) -> int:
    return ctypes.create_string_buffer(x)


if __name__ == "__main__":
    pass
