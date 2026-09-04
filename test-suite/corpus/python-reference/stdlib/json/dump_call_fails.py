"""Test json.dump L5 — negative: caller can't discharge requires.

Documents the soundness path: callers that don't establish the
function's precondition fail to verify under full proof. The
corpus runner uses `--no-proof` for fast iteration; the failure
mode is exercised manually with `--proof`.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import json  # noqa: F401


#@ ensures True
# (#44) `json.dump(obj, fp)` takes TWO arguments and returns None. This driver
# passed ONE and returned the result into an `int`, so it died at
# "call to 'dump' passes 1 positional argument(s) but parameter 'fp' has no
# default (arity 2)" — a generated-test defect, not an emitter one.
def use_dump_unsafe(x: int) -> None:
    json.dump(x, x)


if __name__ == "__main__":
    pass
