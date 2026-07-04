"""0780 — NEGATIVE: the MULTI-slot per-field guard is LOAD-BEARING (cleared-pack item 1).

# pycsl-expected: FAIL

Same faithful `>HI` (u16u32) path as 0777, but the SECOND field `b` is allowed OUT
OF the uint32 range (`b <= 5000000000` > 2^32-1). Verification MUST fail:

  1. `struct.pack('>HI', a, b)` lowers to `struct_pack_fu16u32`, whose per-field
     `requires { 0 <= x1 < 4294967296 }` is a call-site VC — UNPROVABLE for
     b in (2^32-1, 5000000000] (faithful: real `struct.pack` RAISES `struct.error`).
  2. Even ignoring (1), the round-trip axiom's antecedent `0 <= x1 < 2^32` does not
     cover b > 2^32-1, so `\result == b` cannot be discharged — it is FALSE there
     (byte truncation; cf. guard_necessity_u16u32: unpack(pack 65536,·)=(0,·)).

That the SAME code with the tighter `b <= 4294967295` bound PROVES (0777) is the
load-bearing proof that the per-field guard is not decoration.
"""
import struct  # noqa


#@ requires 0 <= a and a <= 65535
#@ requires 0 <= b and b <= 5000000000
#@ assigns \nothing
#@ ensures \result == b
#@ proof rocq Pycsl.Struct.Std.round_trip_u16u32
#@ proof lean Pycsl.Struct.Std.round_trip_u16u32
def roundtrip_field1_out_of_range(a: int, b: int) -> int:
    packed = struct.pack('>HI', a, b)
    _out_a, out_b = struct.unpack('>HI', packed)
    return out_b
