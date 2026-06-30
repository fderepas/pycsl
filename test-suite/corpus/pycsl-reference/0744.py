"""Test 0744 — all-string f-string lowers to faithful `string` concat (b14 B2).

An f-string whose EVERY segment is string-typed — literal text plus `str`-typed
interpolations — lowers to a Why3 `string` concatenation chain via `str_concat_op`
(`ensures result = concat a b`), the same bridge as `s + t` (strings-plan Stage 2),
instead of collapsing each segment to an int hash. So a body-faithful contract
relating `\result` to the spec-level concatenation (`+` → `concat`) discharges.

A mixed f-string (any non-string interpolation) keeps the legacy int-hash model,
so this is additive — pre-existing corpus that interpolates non-strings is
byte-identical.
"""
from __future__ import annotations


#@ requires True
#@ ensures \result == name + sep
#@ assigns \nothing
def join2(name: str, sep: str) -> str:
    return f"{name}{sep}"


#@ requires True
#@ ensures \result == "let " + name
#@ assigns \nothing
def let_binding(name: str) -> str:
    return f"let {name}"


if __name__ == "__main__":
    assert join2("a", "b") == "ab"
    assert let_binding("x") == "let x"
    print("PASS")
