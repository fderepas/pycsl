"""Test 0696 — strings: EARLY `return` in a `str`-returning function (10-1732-gap Gap 1).

DEMAND-DRIVER for the `Return_str` machinery. Before this fix the early-return exception
was hardcoded `exception Return int`, so a faithful `string`-returning function with a
`return` BEFORE the tail (here, inside the `if`) failed to type-check: the `raise (Return s)`
carried a `string` while the catch expected `int` ("This expression has type string, but is
expected to have type int").

The fix mirrors the proven `Return_seq` array machinery: a string-returning function with an
early/in-loop return now emits `exception Return_str string`, raises `raise (Return_str s)`,
and catches with `with Return_str r -> r end` (no materialize — `string` is immutable). The
catch hands the payload straight back, so the early and tail returns agree on `string`.

STATUS — **PROVES**. `first_or_empty` returns `t` early when `s` is empty (the `if` branch),
else falls through to the tail `return s`. Both branches return a `str` param, so the
length-nonnegativity postcondition discharges from the `String.length >= 0` law carried by
`\str_length` (via `str_length_op`). This is the NEW capability, not an expected-FAIL probe."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0 and \str_length(t) >= 0
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def first_or_empty(s: str, t: str) -> str:
    if s == "":
        return t        # EARLY return -> raise (Return_str t)
    return s            # tail return
