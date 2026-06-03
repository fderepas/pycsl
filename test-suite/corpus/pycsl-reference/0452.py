# pycsl-flags: --memory-model hoare
"""0452 — byte-content buffer (io.BytesIO shape): a driver constructs the
buffer, writes byte content, reads it back, and proves the content is preserved
(\array_eq). Body-verified, 0 \trusted; hoare model.

This is the "string-content" milestone. Python `bytes`/`bytearray` literals lower
to arrays of code points, so a byte string carries its actual CONTENT (a `str`
literal lowers to an opaque hash and could not). The driver demonstrates two
emitter pieces beyond B1's int-result method-call fix:

  * record construction from a driver builds a type-correct record — the array
    field `buf` defaults to `Array.make 4096 0` (not the int fallback `0`), so
    its `\length >= 4096` class invariant holds at construction.

  * the method's ARRAY-result postcondition `\array_eq(\result, data)`
    propagates to the call site (renamed to the stub's positional param), so
    `echo_bytes` discharges `\array_eq(\result, payload)` from `b.roundtrip`.

The contract proves the round-trip for EVERY payload (≤ 512 bytes) — strictly
stronger than one literal; PyCSL contracts cannot name a `b"..."` literal
(byte literals aren't in the contract expression grammar). A concrete literal is
checked at runtime below.
"""


#@ class invariant \length(self.buf) >= 4096
class BytesIO:
    def __init__(self):
        self.buf: list = bytearray(4096)

    #@ requires \length(data) <= 512
    #@ assigns self.buf
    #@ ensures \array_eq(\result, data)
    def roundtrip(self, data: list) -> list:
        n = len(data)
        self.buf[0:n] = data
        return self.buf[0:n]


#@ requires \length(payload) <= 512
#@ ensures \array_eq(\result, payload)
#@ assigns \nothing
def echo_bytes(payload: list) -> list:
    b = BytesIO()
    return b.roundtrip(payload)


if __name__ == "__main__":
    assert echo_bytes(b"PyCSL\n") == list(b"PyCSL\n")
    print("PASS")
