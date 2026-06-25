"""Runtime gate LR3 — no enforcement (the Literal shim is identity).

Spec clause LR3 (literal-twoplane-spec.md §2.1): the runtime does NOT check
that a value stored under a `Literal[v1, ..., vn]` annotation is one of
`v1..vn`. The Literal shim (per the §12.9 surface,
`src/pycsl_lib/typ/__init__.py`) is identity — it discharges for ANY value,
regardless of value-set membership.

Per LR7, a faithful shim performs no validation: the identity postcondition
`#@ ensures \\result == val` must discharge for every call. This driver
calls the `Literal` shim directly with values that are NOT in the declared
value set {1, 2} — a string, a list, None — and expects the identity
postcondition to discharge regardless.

Expected (from spec): PASS — the shim performs no enforcement; identity
discharges regardless of value type or value-set membership.
"""

from pycsl_lib.typ import Literal


#@ ensures \result == val
def call_string(val) -> int:
    return Literal(1, 2, val)


#@ ensures \result == val
def call_list(val) -> int:
    return Literal(1, 2, val)


#@ ensures \result == val
def call_none(val) -> int:
    return Literal(1, 2, val)


if __name__ == "__main__":
    assert call_string("not-in-value-set") == "not-in-value-set"
    assert call_list([1, 2, 3]) == [1, 2, 3]
    assert call_none(None) is None
    print("PASS")
