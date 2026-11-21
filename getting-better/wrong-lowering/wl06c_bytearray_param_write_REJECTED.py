"""WL-06c WRITE-POSTURE (T9) — a `bytearray` PARAMETER element write `b[i] = v` is
REJECTED (fail-closed). Verdict: REJECTED.

The implicit byte-RANGE invariant is emitted as an ENTRY precondition. A caller-visible
element write to a `bytearray` PARAMETER is a frame/aliasing boundary (the SAME one for
which dict/set/record param mutation is rejected, §WL-05), so PyCSL rejects it cleanly
rather than emit an unmodeled caller-visible mutation. Consequently the entry range
invariant is NEVER violated in-body: no bytes/bytearray param element write is emitted
at all (`bytes` is rejected as immutable, WL-06b; a `bytearray` param write is rejected
here). A future faithful caller-visible `bytearray` mutation model would additionally
carry a Python-ValueError obligation `0 <= v < 256` on the write (writing 300 into a
byte buffer raises ValueError)."""
_ = 0


#@ requires 0 <= i and i < len(b)
#@ ensures True
def set_byte_REJECTED(b: bytearray, i: int) -> int:
    """A `bytearray` param element write is a caller-visibility boundary — REJECTED."""
    b[i] = 300  # out-of-range AND caller-visible: rejected fail-closed
    return 0
