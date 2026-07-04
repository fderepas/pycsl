"""0781 — NEGATIVE: the SIGNED range guard is LOAD-BEARING (cleared-pack item 2).

# pycsl-expected: FAIL

Same faithful `>h` (int16) path as 0778, but the argument is allowed OUT of the
int16 range on the POSITIVE side (`x <= 40000` > 32767). Verification MUST fail:

  1. `struct.pack('>h', x)` lowers to `struct_pack_fi16`, whose signed guard
     `requires { -32768 <= x0 < 32768 }` is a call-site VC — UNPROVABLE for
     x in (32767, 40000] (faithful: real `struct.pack` RAISES `struct.error`).
  2. Even ignoring (1), the round-trip axiom's antecedent does not cover x > 32767,
     so `\result == x` cannot be discharged — it is FALSE there (two's-complement
     wrap; cf. guard_necessity_i16: unpack(pack 32768) = -32768 != 32768).

That the SAME code with `x <= 32767` PROVES (0778) is the load-bearing proof.
"""
import struct  # noqa


#@ requires -32768 <= x and x <= 40000
#@ assigns \nothing
#@ ensures \result == x
#@ proof rocq Pycsl.Struct.Std.round_trip_i16
#@ proof lean Pycsl.Struct.Std.round_trip_i16
def roundtrip_i16_out_of_range(x: int) -> int:
    packed = struct.pack('>h', x)
    return struct.unpack('>h', packed)
