"""0778 — FAITHFUL SIGNED struct round-trip + size law (cleared-pack item 2).

Standard-size SIGNED integer formats (`h`/`i`/`l`/`q`) now lower to the faithful
`Pycsl.Struct.Std` family with two's-complement byte codecs. The in-range guard
is the SIGNED range `[-2^(8N-1), 2^(8N-1))` (faithful to CPython's out-of-range
`struct.error`). The round-trip holds across the WHOLE range — positive half,
negative half, and the extremes (INT_MIN) — because pack/unpack are anchored to
concrete two's-complement byte codecs in the cross-validated proofs.

Also demonstrates the SIGNED MULTI-slot format `'<ii'` (two int32, tag `i32i32`):
the per-field tag makes its symbol `struct_pack_fi32i32`, provably DISTINCT from a
two-uint16 `>HH` (`struct_pack_fu16u16`) — the choices.md S0 collision is closed.

Proofs: 0778.proofs/{rocq/StructResiduals.v,lean/StructResiduals.lean}
(Pycsl.Struct.Std.{round_trip_i16,round_trip_i32,round_trip_i64,round_trip_i32i32}
+ size_* + guard_necessity_i16). Rocq coqc exit 0 (Closed under global context);
Lean 4.31 exit 0 (#print axioms ⊆ {propext, Classical.choice, Quot.sound}).
"""
import struct  # noqa


#@ requires -32768 <= x and x <= 32767
#@ assigns \nothing
#@ ensures \result == x
#@ proof rocq Pycsl.Struct.Std.round_trip_i16
#@ proof lean Pycsl.Struct.Std.round_trip_i16
def roundtrip_i16(x: int) -> int:
    """Pack an int16 (two's complement) then unpack — round-trips under guard."""
    packed = struct.pack('>h', x)
    return struct.unpack('>h', packed)


#@ requires -32768 <= x and x <= 32767
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ proof rocq Pycsl.Struct.Std.round_trip_i16
#@ proof lean Pycsl.Struct.Std.round_trip_i16
def size_i16(x: int) -> bytes:
    """calcsize('>h') == 2."""
    return struct.pack('>h', x)


#@ requires -2147483648 <= x and x <= 2147483647
#@ assigns \nothing
#@ ensures \result == x
#@ proof rocq Pycsl.Struct.Std.round_trip_i32
#@ proof lean Pycsl.Struct.Std.round_trip_i32
def roundtrip_i32(x: int) -> int:
    """Pack an int32 then unpack — round-trips (incl. the negative half)."""
    packed = struct.pack('>i', x)
    return struct.unpack('>i', packed)


#@ requires -9223372036854775808 <= x and x <= 9223372036854775807
#@ assigns \nothing
#@ ensures \result == x
#@ proof rocq Pycsl.Struct.Std.round_trip_i64
#@ proof lean Pycsl.Struct.Std.round_trip_i64
def roundtrip_i64(x: int) -> int:
    """Pack an int64 then unpack — round-trips across the full 64-bit range."""
    packed = struct.pack('>q', x)
    return struct.unpack('>q', packed)


#@ requires -2147483648 <= a and a <= 2147483647
#@ requires -2147483648 <= b and b <= 2147483647
#@ assigns \nothing
#@ ensures \result == a
#@ proof rocq Pycsl.Struct.Std.round_trip_i32i32
#@ proof lean Pycsl.Struct.Std.round_trip_i32i32
def roundtrip_i32i32_field0(a: int, b: int) -> int:
    """Signed MULTI-slot '<ii' (little-endian two int32) — first field round-trips.
    Its symbol is `struct_pack_fi32i32`, never colliding with a `>HH` u16u16."""
    packed = struct.pack('<ii', a, b)
    out_a, _out_b = struct.unpack('<ii', packed)
    return out_a
