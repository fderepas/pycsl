"""0753 — FAITHFUL guarded struct round-trip + size law (cleared-pack S1-S3).

`struct.pack`/`struct.unpack` of a SINGLE standard-size unsigned-int slot
('>H' = u16, '>I' = u32) now lower to the byte-faithful `Pycsl.Struct.Std`
family instead of the opaque abstract `struct_{pack,unpack}_iN` symbols:

  * S1 size law  — `len(pack(fmt, x)) == calcsize(fmt)` (pack `val` `ensures`).
  * S2 in-range guard — the `requires 0 <= x < 2^(8N)` is a CALL-SITE VC
    (real `struct.pack` RAISES `struct.error` out-of-range for standard sizes).
  * S3 round-trip — `unpack(fmt, pack(fmt, x)) == x`, discharged by the cited,
    cross-validated round-trip axiom.

Anchored by concrete big-endian base-256 byte-codec proofs (NOT reflexivity
over uninterpreted symbols): 0753.proofs/{rocq/Struct.v,lean/Struct.lean}
(Pycsl.Struct.Std.{round_trip_u16,round_trip_u32}; the same files prove the
size laws and the guard_necessity_u* counterexamples — unpack(pack 65536)=0
!= 65536 — showing the guard is load-bearing; the negative driver 0754 makes
that observable at the PyCSL level). Guard-necessity itself: driver 0754.
"""
import struct  # noqa


#@ requires 0 <= x and x <= 65535
#@ assigns \nothing
#@ ensures \result == x
#@ proof rocq Pycsl.Struct.Std.round_trip_u16
#@ proof lean Pycsl.Struct.Std.round_trip_u16
def roundtrip_u16(x: int) -> int:
    """Pack a uint16 then unpack — the value round-trips under the guard."""
    packed = struct.pack('>H', x)
    return struct.unpack('>H', packed)


#@ requires 0 <= x and x <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ proof rocq Pycsl.Struct.Std.round_trip_u16
#@ proof lean Pycsl.Struct.Std.round_trip_u16
def size_u16(x: int) -> bytes:
    """calcsize('>H') == 2 — the packed buffer is exactly 2 bytes."""
    return struct.pack('>H', x)


#@ requires 0 <= x and x <= 4294967295
#@ assigns \nothing
#@ ensures \result == x
#@ proof rocq Pycsl.Struct.Std.round_trip_u32
#@ proof lean Pycsl.Struct.Std.round_trip_u32
def roundtrip_u32(x: int) -> int:
    """Pack a uint32 then unpack — the value round-trips under the guard."""
    packed = struct.pack('>I', x)
    return struct.unpack('>I', packed)


#@ requires 0 <= x and x <= 4294967295
#@ assigns \nothing
#@ ensures \length(\result) == 4
#@ proof rocq Pycsl.Struct.Std.round_trip_u32
#@ proof lean Pycsl.Struct.Std.round_trip_u32
def size_u32(x: int) -> bytes:
    """calcsize('>I') == 4 — the packed buffer is exactly 4 bytes."""
    return struct.pack('>I', x)
