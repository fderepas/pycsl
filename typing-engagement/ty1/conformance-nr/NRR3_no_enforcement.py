"""Runtime gate NR-R3 — the NoReturn shim does NOT enforce divergence.

Spec clause NR-R3 (noreturn-twoplane-spec.md §2.1 — the central negative
sentence): the Python runtime does NOT check that a `NoReturn`-annotated
function diverges or raises. A function annotated `-> NoReturn` that
RETURNS a value (a program bug) returns at runtime without error; the
runtime does not raise, does not warn, does not trap. The annotation is
documentation, not a runtime contract. (S3 central negative sentence;
resolved by S4 — `NoReturn` is an introspectable alias object, not a check.)

The pycsl_lib shim (`src/pycsl_lib/typ/__init__.py`) defines
`NoReturn = None` — the introspectable alias object with NO validation
(NR-R4). So `def f() -> NoReturn: return 1` evaluates at runtime as
`def f() -> None: return 1` (NoReturn is None), and Python does NOT enforce
the `-> None` return annotation, so `f()` returns 1 without error.

This is a RUNTIME-plane test: it is executed with plain `python3` (NOT
verified by pycsl). The static plane would reject this function (NR2a —
the body returns normally); the runtime plane must NOT.

Expected (from spec): PASS (at runtime) — `f()` returns 1, no error raised
by the shim. The shim performs no enforcement of divergence (NR-R3).
"""

from pycsl_lib.typ import NoReturn


def f() -> NoReturn:   # NoReturn is None at runtime (the alias object)
    return 1           # a bug: NoReturn should not return — but runtime allows it


if __name__ == "__main__":
    result = f()
    # The shim must NOT enforce divergence: f() returns 1 without error.
    assert result == 1, f"expected 1, got {result}"
    # NR-R1/NR-R2: NoReturn is the introspectable alias object (None here),
    # NOT a distinct runtime type and NOT a check.
    assert NoReturn is None
    print("PASS")
