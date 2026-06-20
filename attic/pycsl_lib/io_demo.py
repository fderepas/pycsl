"""Formal driver for the io stub: thin annotated wrappers over io's stream
helpers, each contract discharged from the callee's `ensures`. Verified
end-to-end (no `\trusted`) via `pycsl src/pycsl_lib/io_demo.py`."""
import io
from io import BytesIO   # name-import form so the class record + method
                         # contracts cross the module boundary (a module-
                         # qualified `io.BytesIO()` is not resolved to the
                         # imported record — it lowers to an opaque op)


#@ requires file >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_open(file: int) -> int:
    """Open a file descriptor; returns a non-negative handle."""
    return io.open(file, 0, 0, 0, 0, 0, 1)


#@ requires path >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_open_code(path: int) -> int:
    """Open a path in binary read mode; returns a non-negative handle."""
    return io.open_code(path)


#@ requires encoding >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def demo_text_encoding(encoding: int) -> int:
    """Resolve a text encoding; returns a non-negative result."""
    return io.text_encoding(encoding, 0)


# ── BytesIO content round-trip (string-content milestone) ───────────
# Construct an io.BytesIO, write byte content, read it back, and prove the
# content is preserved (\array_eq). The driver discharges this from BytesIO's
# method contract — record construction builds the array buffer, and the
# method's array-result postcondition propagates to the call site.

#@ requires \length(payload) <= 512
#@ ensures \array_eq(\result, payload)
#@ assigns \nothing
def demo_bytesio_roundtrip(payload: list) -> list:
    buf = BytesIO()
    return buf.roundtrip(payload)


if __name__ == "__main__":
    # Runtime check with a literal byte string. The *contract* above proves the
    # round-trip for EVERY payload (≤ 512 bytes) — strictly stronger than this
    # one literal — because PyCSL contracts cannot name a `b"..."` literal
    # directly (byte literals aren't part of the contract expression grammar).
    assert demo_bytesio_roundtrip(b"PyCSL\n") == list(b"PyCSL\n")
    print("PASS")
