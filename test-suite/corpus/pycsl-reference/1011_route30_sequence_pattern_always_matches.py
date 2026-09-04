"""Test 1011 — ROUTE #30 negative witness: an unrecognized `match` pattern
lowered to an UNCONDITIONALLY TRUE arm condition, in the DEFAULT model.

FALSE OF THE PROGRAM: `x` is 5, an int never matches a SEQUENCE pattern, and
Python returns 2.

At the parent commit c4233fed this printed `[+] Verification SUCCESS! All
contracts formally proven.` The emission was literally

    if true then begin 1 end else begin 2 end

because `module6_whyml/expressions.py::_match_pattern_cond` handled only
`Wildcard`/`Value`/`Capture`/`Or` and ended in a bare `return "true"`, while
`Module5_IREmitter._py_pattern_to_ir` emits SEVEN kinds. No `--memory-model`
flag, no spec atom — ordinary modern Python in the default configuration.

`"false"` would NOT have been a fix: on a subject the pattern really does match
it skips the arm and the model takes a later one, so the same false-contract
proof returns with the arms swapped. The condition is UNKNOWN, and a boolean has
no room for that, so the pipeline REFUSES
(`PYCSL-R30-UNINTERPRETED-PATTERN`).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires x == 5
#@ ensures \result == 1
#@ assigns \nothing
def f(x: int) -> int:
    match x:
        case [1, 2]:
            return 1
        case _:
            return 2
