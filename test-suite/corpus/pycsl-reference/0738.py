"""Test 0738 — `-> NoReturn` witness (NR1 / NR2a).

typing-engagement ty1 (28-0000-typing-spec-4): `-> NoReturn` (PEP 484) lowers
to a `false` postcondition (NR1) — the function never returns normally. The
body raises (NR2a — no normal exit), so the `ensures { false }` VC discharges
by the absence of a normal-exit path. NR4: the non-vacuity gate exempts this
function (its `false` post is the SPEC, not a vacuity signal).
"""
from typing import NoReturn


def f() -> NoReturn:
    raise Exception()

if __name__ == "__main__":
    try:
        f()
    except Exception:
        print("PASS")
