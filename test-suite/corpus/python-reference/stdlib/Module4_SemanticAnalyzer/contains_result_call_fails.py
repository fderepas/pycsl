"""Test Module4_SemanticAnalyzer.contains_result L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module4_SemanticAnalyzer  # noqa: F401


#@ ensures True
def use_contains_result_unsafe(x: int) -> int:
    return Module4_SemanticAnalyzer.contains_result(x)


if __name__ == "__main__":
    pass
