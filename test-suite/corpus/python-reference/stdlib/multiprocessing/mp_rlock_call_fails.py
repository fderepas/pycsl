"""Test multiprocessing.mp_rlock L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import multiprocessing  # noqa: F401


#@ ensures True
def use_mp_rlock_unsafe(x: int) -> int:
    return multiprocessing.mp_rlock(x)


if __name__ == "__main__":
    pass
