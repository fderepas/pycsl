"""Runtime gate FR3 — no enforcement (the Final shim is identity).

Spec clause FR3 (final-twoplane-spec.md §2.1): the runtime does NOT check
that a name annotated `Final[T]` is written only once or that an attribute
annotated `Final[T]` is written only in `__init__`. Reassigning a `Final`
name at runtime SUCCEEDS (no error): the assignment executes, the name is
rebound, and no exception is raised. The write-once / `__init__`-only
restriction is a static-plane judgment ONLY.

Per the §12.10 surface, `src/pycsl_lib/typ/__init__.py` provides a
`Final(x0, x1, val)` shim with `#@ ensures \\result == val` — identity,
no validation (FR1–FR6, FD2 no-blend). This driver calls the `Final`
shim directly with values that would VIOLATE the static write-policy (a
reassignment at runtime — exactly the case F1 rejects statically) and
expects the identity postcondition to discharge regardless. The shim must
NOT enforce write-once (FR3): a reassignment at runtime is allowed.

Expected (from spec): PASS — the shim performs no enforcement; identity
discharges regardless of value or write-policy violation.
"""

from pycsl_lib.typ import Final


#@ ensures \result == val
def call_int(val) -> int:
    return Final(int, None, val)


#@ ensures \result == val
def call_string(val) -> int:
    return Final(int, None, val)


#@ ensures \result == val
def call_list(val) -> int:
    return Final(int, None, val)


if __name__ == "__main__":
    # A reassignment at runtime — the static plane would reject this (F1),
    # but the runtime shim must NOT enforce write-once (FR3).
    v = 5
    v = 6  # runtime reassignment — succeeds, no error
    assert call_int(v) == 6
    assert call_string("not-an-int") == "not-an-int"
    assert call_list([1, 2, 3]) == [1, 2, 3]
    print("PASS")
