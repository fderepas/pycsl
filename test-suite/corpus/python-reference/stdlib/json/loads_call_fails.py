"""Test json.loads L5 — negative: caller can't discharge requires.

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
# (#44) `json.loads` DECLARES `raises JSONDecodeError` and `raises TypeError`
# in its stub, so a driver calling it must declare them too — otherwise the
# emission is 'this expression raises unlisted exception ...'. The STUB is
# honest here and the driver was under-specified.
#@ raises JSONDecodeError when True
#@ raises TypeError when True
def use_loads_unsafe(x: int) -> int:
    return json.loads(x)


if __name__ == "__main__":
    pass
