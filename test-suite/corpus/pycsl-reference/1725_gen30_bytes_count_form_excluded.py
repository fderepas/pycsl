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

`bytes` is therefore excluded from the count form and this file must FAIL. The underlying
gap is pre-existing and separate: `PYCSL-SEM-SUBSCRIPT`'s immutability refusal keys on the
SYMBOL TABLE typing the local `bytes`, which it does not do for `b = bytes(2)`, so nothing
but the typing stops the store.

>>> A LOWERING FIX MUST RE-RUN THE REFUSAL THE OLD SHAPE WAS ACCIDENTALLY ENFORCING.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 7
def bytes_immutable_still_refused() -> int:
    b = bytes(2)
    b[0] = 7
    return b[0]
