"""Test argparse.set_defaults L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import argparse  # noqa: F401


#@ ensures True
def use_set_defaults_unsafe(x: int) -> int:
    return argparse.set_defaults(x)


if __name__ == "__main__":
    pass
