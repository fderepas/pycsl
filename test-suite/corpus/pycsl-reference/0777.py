"""0777 — FAITHFUL MULTI-SLOT struct round-trip + size law (cleared-pack item 1).

`struct.pack`/`struct.unpack` of a MULTI-slot standard-size format now lower to
the byte-faithful `Pycsl.Struct.Std` family with a PER-FIELD width/signedness tag
— closing the choices.md S0 collision (the legacy `slot_id` encoded only WhyML
*types*, so `>HH` (two uint16) and `<ii` (two int32) both became `struct_pack_i2`;
the per-field tag makes them `struct_pack_fu16u16` vs `struct_pack_fi32i32`).

Here the format is `'>HI'` = (uint16, uint32), tag `u16u32`, 6 bytes:

  * S1 size law  — `len(pack('>HI', a, b)) == calcsize('>HI') == 6`.
  * S2 per-field in-range guards — `0 <= a < 2^16` AND `0 <= b < 2^32` (both are
    CALL-SITE VCs; real `struct.pack` RAISES `struct.error` out-of-range).
  * S3 round-trip — `unpack('>HI', pack('>HI', a, b)) == (a, b)`, each field
    projected through the cited tuple round-trip axiom.

Anchored by concrete big-endian base-256 byte-codec proofs (NOT reflexivity over
uninterpreted symbols): 0777.proofs/{rocq/StructResiduals.v,lean/StructResiduals.lean}
(Pycsl.Struct.Std.{round_trip_u16u32,size_u16u32,guard_necessity_u16u32}).
"""
import struct  # noqa


#@ requires 0 <= a and a <= 65535
#@ requires 0 <= b and b <= 4294967295
#@ assigns \nothing
#@ ensures \result == a
#@ proof rocq Pycsl.Struct.Std.round_trip_u16u32
#@ proof lean Pycsl.Struct.Std.round_trip_u16u32
def roundtrip_field0(a: int, b: int) -> int:
    """Pack (u16, u32) then unpack — the FIRST field round-trips under guards."""
    packed = struct.pack('>HI', a, b)
    out_a, _out_b = struct.unpack('>HI', packed)
    return out_a


#@ requires 0 <= a and a <= 65535
#@ requires 0 <= b and b <= 4294967295
#@ assigns \nothing
#@ ensures \result == b
#@ proof rocq Pycsl.Struct.Std.round_trip_u16u32
#@ proof lean Pycsl.Struct.Std.round_trip_u16u32
def roundtrip_field1(a: int, b: int) -> int:
    """Pack (u16, u32) then unpack — the SECOND field round-trips under guards."""
    packed = struct.pack('>HI', a, b)
    _out_a, out_b = struct.unpack('>HI', packed)
    return out_b


#@ requires 0 <= a and a <= 65535
#@ requires 0 <= b and b <= 4294967295
#@ assigns \nothing
#@ ensures \length(\result) == 6
#@ proof rocq Pycsl.Struct.Std.round_trip_u16u32
#@ proof lean Pycsl.Struct.Std.round_trip_u16u32
def size_u16u32(a: int, b: int) -> bytes:
    """calcsize('>HI') == 6 — the packed buffer is exactly 6 bytes."""
    return struct.pack('>HI', a, b)
