"""Test Module5_IREmitter.scan_2d_in_stmt L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module5_IREmitter  # noqa: F401


#@ ensures True
def use_scan_2d_in_stmt_unsafe(x: int) -> int:
    return Module5_IREmitter.scan_2d_in_stmt(x)


if __name__ == "__main__":
    pass
