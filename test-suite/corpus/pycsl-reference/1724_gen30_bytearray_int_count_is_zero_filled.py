r"""Test 1724 — gen #30: `bytearray(n)` / `bytes(n)` as a LOCAL now lowers to n zero bytes.

Found by AUDITING A REFUSAL'S ADVICE (the route #90 class). `PYCSL-SEM-SUBSCRIPT` refuses
`b[i] = v` on an immutable `bytes` and advises "Use a `bytearray` for a mutable byte
buffer". Following that advice with the standard spelling did not work:

    b = bytearray(2)        # emitted `bytearray_new 2` against
    b[0] = 7                # `val bytearray_new (x: array int)`
    return b[0]             # -> Why3: "has type int, but is expected to have type array"

Fail-closed, and the default-on typecheck gate is what caught it — but the advice pointed
at a spelling that could not be compiled, while `bytearray(b"\x00\x00")` and
`bytearray([0, 0])` both worked.

The faithful lowering already existed ten lines away in the FIELD path: `self.disk =
bytearray(4096)` emits `Array.make 4096 0` (corpus 0461). CPython agrees — `bytearray(n)`
is n zero bytes — so the local path now gives the same answer, restricted to an argument
the IR says is a COUNT (a literal `Number`, or a `Var` the symbol table types `int`), so an
array-valued argument still takes the element-preserving `*_new` path (corpus 0616).

This file pins BOTH halves: the count form is zero-filled and writable, and the
array-valued form still preserves elements.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == 7
def written() -> int:
    b = bytearray(2)
    b[0] = 7
    return b[0]


#@ ensures \result == 0
def zero_filled() -> int:
    b = bytearray(4)
    return b[3]


#@ ensures \length(\result) == 3
#@ assigns \nothing
def elements_preserved() -> list:
    return bytes([1, 2, 3])
