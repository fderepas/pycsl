"""Static gate NR2a (negative) — a NoReturn body that returns normally is a static ERROR.

Spec clause NR2a (noreturn-twoplane-spec.md §1.0): a function carrying the
`diverges`/`false`-postcondition flag MUST have a body with a potentially-
diverging construct (`While`/`For`/`CriticalSection`/`Call`) or a guaranteed
raise. A `NoReturn` annotation on a body that provably terminates (here: a
bare `return 1`) is a static ERROR — the `false` postcondition is genuinely
unprovable (not vacuous, just wrong): the body has a normal-exit path, so
`false` cannot hold at that exit.

Expected (from spec): FAIL (PIPELINE ERROR) — the body-supports-divergence
check (`_check_noreturn` / `_check_diverges`) rejects the `return` statement
at the semantic-analysis stage, before any WhyML is emitted. The runtime
would execute the `return` (NR-R3); the rejection is static-plane only
(NR-D1 divergence).
"""

from typing import NoReturn


def f() -> NoReturn:
    return 1


if __name__ == "__main__":
    # Runtime would return 1 (NR-R3 — no enforcement); the static gate must
    # FAIL because of the NR2a body-does-not-diverge violation.
    print(f())  # noqa: runtime-only; never reached under pycsl
