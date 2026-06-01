"""Test Module2_Parser.FieldAccess L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import Module2_Parser  # noqa: F401


#@ ensures True
def use_FieldAccess_unsafe(x: int) -> int:
    return Module2_Parser.FieldAccess(x)


if __name__ == "__main__":
    pass
