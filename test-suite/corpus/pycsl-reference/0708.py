"""Test 0708 — string ↔ fixed-width null-padded byte-field codec round-trip.

string-codec Phase A' (14-string-field-codec-plan.md §2.5): the foundation primitive for
modeling Python `struct '>Ns'` fields (dirent names, symlink targets, file content) as REAL
string semantics instead of opaque abstract decodes. `field_to_str(buf, off, width)` is the
null-terminated name in the `width`-byte field at `off`. The ENCODE→DECODE round-trip — a
name written byte-for-byte into the field, null-terminated, with no embedded null, decodes
back to exactly that name — is the load-bearing fact the heavy directory syscalls need
(`slot_name(disk, 5, k) == pathname`).

It is NOT SMT-dischargeable: the proof is by string EXTENSIONALITY over Why3's axiomatic
`string.String`, which E-match-explodes (Phase A measured ~23M steps → timeout). So it is a
CITED axiom (`UnixFs.Field.field_to_str_round_trip`) — SMT only APPLIES it here (O(1)),
while the extensionality reasoning is discharged once, offline, in the cross-validated
Rocq + Lean proofs (FieldToStrRoundTrip.{v,lean}). This test confirms the axiom APPLIES
fast: the empty-body VC is exactly the axiom instantiated under the encoding preconditions.

`ord(name[i])` here lowers (in the contract / logic context) to `Char.code (Char.get ...)`,
the pure `string.Char` form — the string-codec Phase A' context-dependent `ord`/`chr`
lowering — so it matches the axiom's antecedent directly.
"""

from typing import List


#@ requires 0 <= len(name)
#@ requires len(name) <= width
#@ requires \forall i: int; (0 <= i and i < len(name)) ==> ord(name[i]) != 0
#@ requires \forall i: int; (0 <= i and i < len(name)) ==> buf[off + i] == ord(name[i])
#@ requires len(name) < width ==> buf[off + len(name)] == 0
#@ ensures field_to_str(buf, off, width) == name
#@ proof rocq UnixFs.Field.field_to_str_round_trip
#@ proof lean UnixFs.Field.field_to_str_round_trip
def decode_field(buf: List[int], off: int, width: int, name: str) -> None:
    pass


# The END-TO-END round-trip: ENCODE a name into a fresh 30-byte '>30s' field (the
# symlink-target / dirent-name shape, the same loop as the os `_pad_name`), then DECODE
# it back with `field_to_str` == name. The encode loop establishes the codec axiom's
# byte preconditions in-body (out[i] == ord(name[i]); null-padded tail), and the cited
# round-trip axiom closes the decode. `ord(name[i])` lowers to `char_code_at name i` in
# the body and `Char.code (Char.get name i)` in the loop invariant / contract — the
# string-codec Phase A' direct char lowering that makes the two match atom-for-atom (no
# `String.substring` detour, which would E-match-explode). This is the foundation for the
# os symlink-target → readlink round-trip and the file content_round_trip.
#@ requires len(name) <= 30
#@ requires \forall i: int; (0 <= i and i < len(name)) ==> ord(name[i]) != 0
#@ ensures field_to_str(\result, 0, 30) == name
#@ proof rocq UnixFs.Field.field_to_str_round_trip
#@ proof lean UnixFs.Field.field_to_str_round_trip
def encode_field(name: str) -> list:
    out = [0] * 30
    m = len(name)
    #@ loop invariant 0 <= i and i <= m
    #@ loop invariant m <= 30
    #@ loop invariant m <= len(name)
    #@ loop invariant \forall j: int; (0 <= j and j < i) ==> out[j] == ord(name[j])
    #@ loop invariant \forall j: int; (i <= j and j < 30) ==> out[j] == 0
    #@ loop variant m - i
    for i in range(m):
        out[i] = ord(name[i])
    return out
