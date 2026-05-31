"""Test enum.show_flag_values L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import enum  # noqa: F401


#@ ensures True
def use_show_flag_values_unsafe(x: int) -> int:
    return enum.show_flag_values(x)


if __name__ == "__main__":
    pass
