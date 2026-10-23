r"""Test 1809 — ROUTE #217, THE EXPLOIT ARM (now REFUSED): an item store into a local bound
from the `bytes(...)` CONSTRUCTOR.

AT THE PARENT COMMIT THIS FILE PROVED `\result == 9`. CPython raises
`TypeError: 'bytes' object does not support item assignment`, so the model was proving a
postcondition about a program that cannot run — the same shape as route #215.

WHY IT PROVED. `PYCSL-SEM-SUBSCRIPT`'s immutability refusal keys on the SYMBOL TABLE typing
the local `"bytes"`, and `_build_function_symbol_table` typed a local bound from a
`bytes(...)` CONSTRUCTOR as `"Any"` — only a bare bytes LITERAL (`b = b"abc"`) got the
`"bytes"` classification. Witness 1725 pins the COUNT form `b = bytes(2)` and its docstring
names this as "pre-existing and separate"; THE ITERABLE FORM HAD NO WITNESS AT ALL, and it
is the form that actually occurs — eight of the nine corpus sites.

CLOSED by typing a `bytes(...)`-bound local as `"bytes"`, one branch in
`_build_function_symbol_table`, whose mirror twin is `\trusted` — no mirror edit, no
re-proof. Byte-diff over the whole corpus, both sides emitted fresh: 1303 baseline,
0 MOVED, 0 APPEARED, exactly 1 GONE (1725, which is expected-FAIL either way and now fails
by the REFUSAL rather than by ill-typedness).

Controls: 1810 (`bytearray` is MUTABLE and must still verify) and the read-only form
`b = bytes([65, 66, 67]); return b[0]`, which still verifies.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 9
def f() -> int:
    b = bytes([1, 2, 3])
    b[0] = 9
    return b[0]
