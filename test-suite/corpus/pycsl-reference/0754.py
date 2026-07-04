"""0754 — NEGATIVE: the struct round-trip guard is LOAD-BEARING (cleared-pack S2).

# pycsl-expected: FAIL

Same faithful `Pycsl.Struct.Std` u16 path as 0753, but the argument is allowed
OUT OF the uint16 range (`x <= 100000`). Verification MUST fail, for two honest
reasons that both trace to the missing in-range guard:

  1. `struct.pack('>H', x)` lowers to `struct_pack_fu16`, whose `requires
     { 0 <= x0 < 65536 }` is a call-site VC — UNPROVABLE for x in (65535,100000]
     (faithful: real `struct.pack` RAISES `struct.error` there).
  2. Even ignoring (1), the round-trip axiom's antecedent `0 <= x0 < 65536` does
     not cover x > 65535, so `\result == x` cannot be discharged — because it is
     FALSE (`unpack(pack 65536) == 0 != 65536`, the guard_necessity_u16
     counterexample proven in 0753.proofs).

Drop the `x <= 65535` bound from 0753's `roundtrip_u16` and this is what you get:
the guard is not decoration — without it the law is a lie. That the SAME code
with the tighter `x <= 65535` bound PROVES (0753) is the load-bearing proof.
"""
import struct  # noqa


#@ requires 0 <= x and x <= 100000
#@ assigns \nothing
#@ ensures \result == x
#@ proof rocq Pycsl.Struct.Std.round_trip_u16
#@ proof lean Pycsl.Struct.Std.round_trip_u16
def roundtrip_u16_out_of_range(x: int) -> int:
    packed = struct.pack('>H', x)
    return struct.unpack('>H', packed)
