"""0779 — FAITHFUL fixed-bytes struct round-trip + size law (cleared-pack item 3).

A single fixed-bytes `s` slot (`'>4s'`, 4 bytes) lowers to the faithful array-
identity family `struct_{pack,unpack}_fs4`:

  * S1 size law  — `len(pack('>4s', d)) == 4`.
  * S2 guard     — `len(d) == 4` (the round-trip precondition; `struct.pack`
    truncates/null-pads otherwise, so identity holds only at the exact width).
  * S3 round-trip — `unpack('>4s', pack('>4s', d)) == d` (byte-array identity).

Anchored by the trivial list-identity byte-codec proof
0779.proofs/{rocq/StructResiduals.v,lean/StructResiduals.lean}
(Pycsl.Struct.Std.{round_trip_s4,size_s4}: `firstn 4 d = d` when `length d = 4`).
"""
import struct  # noqa


#@ requires \length(d) == 4
#@ assigns \nothing
#@ ensures \result == d
#@ proof rocq Pycsl.Struct.Std.round_trip_s4
#@ proof lean Pycsl.Struct.Std.round_trip_s4
def roundtrip_s4(d: bytes) -> bytes:
    """Pack a 4-byte buffer verbatim then unpack — the bytes round-trip."""
    packed = struct.pack('>4s', d)
    return struct.unpack('>4s', packed)


#@ requires \length(d) == 4
#@ assigns \nothing
#@ ensures \length(\result) == 4
#@ proof rocq Pycsl.Struct.Std.round_trip_s4
#@ proof lean Pycsl.Struct.Std.round_trip_s4
def size_s4(d: bytes) -> bytes:
    """calcsize('>4s') == 4 — the packed buffer is exactly 4 bytes."""
    return struct.pack('>4s', d)
