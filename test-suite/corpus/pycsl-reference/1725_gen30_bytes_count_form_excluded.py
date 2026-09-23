r"""Test 1725 — gen #30 NEGATIVE TWIN of 1724: `bytes` is excluded from the count form, and
this is the file that says why.

The first version of 1724's fix lowered `bytes(n)` as well as `bytearray(n)`. FOUR MINUTES
LATER, re-running the very refusal the fix was about showed

    b = bytes(2)
    b[0] = 7
    return b[0]

PROVING `\result == 7`, while CPython raises `TypeError: 'bytes' object does not support
item assignment`. At the PARENT COMMIT that same program FAILED — so the ILL-TYPEDNESS had
been doing the enforcing (`bytes_new 2` against `val bytes_new (x: array int)`), and making
the lowering faithful removed the accident.

`bytes` was therefore excluded from the count form and this file must FAIL. The underlying
gap was pre-existing and separate: `PYCSL-SEM-SUBSCRIPT`'s immutability refusal keys on the
SYMBOL TABLE typing the local `bytes`, which it did not do for `b = bytes(2)`, so nothing
but the typing stopped the store.

>>> A LOWERING FIX MUST RE-RUN THE REFUSAL THE OLD SHAPE WAS ACCIDENTALLY ENFORCING.

GEN #31 — THE EXCLUSION IS LIFTED, AND THIS FILE STILL FAILS, FOR A BETTER REASON. Route
#217 closed the underlying gap: a local bound from the `bytes(...)` constructor is now typed
`"bytes"` in `_build_function_symbol_table`, so the immutability refusal fires. Re-run, not
inherited:

    [!] PIPELINE ERROR: Subscript assignment to immutable 'bytes' variable 'b' in function
    'bytes_immutable_still_refused' — a Python `bytes` object does not support item
    assignment (TypeError). Use a `bytearray` for a mutable byte buffer.

So this file's verdict is unchanged (FAIL) and its MEANING has moved from "fails because
the emission is ill-typed" to "fails because the compiler refuses the store" — which is the
whole point of the pairing, and the reason the exclusion could be lifted at all. `bytes(n)`
now lowers to `Array.make n 0` exactly as `bytearray(n)` does, and CPython agrees that
`bytes(2)[0]` is 0 (corpus 1818 pins it; 1819 is the false twin).

Lesson (f3), which this file is now an instance of in both directions: an exclusion you
never re-test is a guess, and a MENTIONED exclusion that was never re-checked is a guess
wearing a reason. This one named its own precondition — and the precondition came true.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 7
def bytes_immutable_still_refused() -> int:
    b = bytes(2)
    b[0] = 7
    return b[0]
