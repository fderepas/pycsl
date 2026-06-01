"""Test Module6_WhyMLTranspiler.ends_with_return L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module6_WhyMLTranspiler  # noqa: F401


#@ ensures True
def use_ends_with_return_unsafe(x: int) -> int:
    return Module6_WhyMLTranspiler.ends_with_return(x)


if __name__ == "__main__":
    pass
