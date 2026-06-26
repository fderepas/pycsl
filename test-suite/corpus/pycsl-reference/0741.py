"""Test 0741 — `-> NoReturn` NR4 vacuity-gate exemption.

typing-engagement ty1 (28-0000-typing-spec-4): a declared-`NoReturn` function
carries a `false` postcondition BY DESIGN (NR1). The non-vacuity gate
(`--check-vacuity`) exempts it (NR4) — the exemption is keyed on the IR
`is_noreturn` flag (from the `-> NoReturn` annotation), NOT on the inferred
postcondition. This test passes `--check-vacuity` without being flagged.

Run with: pycsl 0741.py --check-vacuity
"""
from typing import NoReturn


def f() -> NoReturn:
    raise Exception()

if __name__ == "__main__":
    try:
        f()
    except Exception:
        print("PASS")
