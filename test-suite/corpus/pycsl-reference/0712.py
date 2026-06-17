"""Test 0712 — directory per-slot NAME-field byte->decode (Gap-5 keystone, STRING half).

The byte->decode primitive for the directory per-slot NAME field — the string twin of
0711's `slot_inode` (the inode half). A directory slot is 32 bytes (`struct '>H30s'`): a
2-byte big-endian inode field followed by a 30-byte null-padded name field. `slot_name(disk,
blk, k)` is the decoded name in the 30-byte field at byte offset `blk*512 + 32*k + 2` of the
disk — i.e. EXACTLY `field_to_str(disk, blk*512 + 32*k + 2, 30)` (the SAME scan-to-first-null
`'>Ns'` decode validated in 0708's FieldToStrRoundTrip).

This file BUILDS the string-half keystone ON the already-merged `field_to_str` codec: a
BRIDGE axiom (`UnixFs.Dir.slot_name_byte_decode`) states `slot_name(disk,blk,k) ==
field_to_str(disk, blk*512+32*k+2, 30)`, and the END-TO-END write rung composes it with the
cited `field_to_str_round_trip` to conclude `slot_name(disk,blk,k) == name` after a fresh
dirent name has been blitted into the slot's name field. This is the string twin of 0711's
inode write rung; it is the BANKED primitive the future directory write helpers need.

NOTE — NOT a trust retirement. This primitive does NOT by itself retire any dirscan
`\trusted`; retiring a dirscan trust (Step 2) remains separately blocked on the
invariant-maintenance E-matching. This file banks the byte-decode keystone only.

WALL CHARACTER: UNLIKE 0711's inode decode (a finite 2-byte equation SMT applies in O(1)),
the name decode's `slot_name == name` conclusion is the field_to_str round-trip, by string
EXTENSIONALITY over the 30-byte scan — the measured ~23M-step Alt-Ergo/Z3 string wall. So
BOTH the bridge and the round-trip are CITED axioms; SMT only APPLIES them (each O(1)), while
the extensionality reasoning is discharged offline in the cross-validated Rocq + Lean proofs.

TRIGGER DISCIPLINE: the bridge axiom is keyed on the BYTE expression
`[disk[blk*512 + 32*k + 2]]` (the FIRST name-field byte), NOT on `slot_name` — so it fires
only where an explicit name-field-byte term is present (a write helper's post-blit state),
never on the ubiquitous abstract `slot_name` atoms the uniq / dir_lookup / scan axiom web
triggers on (concretizing the abstract symbol globally would E-match-explode — measured).

Cross-validated by SlotNameByteDecode.{v,lean} (theorem slot_name_byte_decode): slot_name is
defined as `field_to_str (slot_off blk k + 2) 30` over the scan-to-first-null model, and the
write-direction round-trip is proved by string extensionality. Rocq 8.20.1: Closed under the
global context (only the abstract Section Variable rd, 0 Axiom/Admitted); Lean 4.31.0:
"depends on axioms: [propext, Quot.sound]" (subseteq {propext, Quot.sound}).
"""

from typing import List


# The BRIDGE value fact: the abstract per-slot name decode IS the field_to_str of the 30-byte
# name field that starts 2 bytes into the slot. The cited bridge axiom closes the empty-body
# VC under the byte-keyed trigger (the name-field-byte term `disk[blk*512+32*k+2]` in the
# requires makes the trigger present). `slot_name` is the SAME abstract UnixFs.Dir symbol the
# os model's directory helpers / scan axioms use; `field_to_str` is the SAME UnixFs.Field
# codec 0708 validates.
#@ requires disk[blk * 512 + 32 * k + 2] == first
#@ ensures slot_name(disk, blk, k) == field_to_str(disk, blk * 512 + 32 * k + 2, 30)
#@ proof rocq UnixFs.Dir.slot_name_byte_decode
#@ proof lean UnixFs.Dir.slot_name_byte_decode
def slot_name_bridge(disk: List[int], blk: int, k: int, first: int) -> None:
    pass


# The byte-only ENCODE helper: blit a name byte-for-byte into the 30-byte field starting at
# the ARBITRARY offset `off`, null-padding the tail. Its contract is PURE BYTES (no slot_name,
# no field_to_str) — so the byte-keyed bridge trigger is NOT syntactically present in this
# loop's VCs (the trigger pattern is `disk[blk*512+32*k+2]`, which an opaque `off` cannot
# match), and the loop proves as a clean byte loop. This is the SAME encode loop as the os
# `_pad_name`. (Structural lesson: keep the string axiom OUT of the byte-blit loop — pass the
# field offset opaquely so the trigger fires only at the decode site, never per-iteration.)
#@ requires off >= 0
#@ requires len(name) <= 30
#@ requires \valid(disk, off + 30)
#@ assigns disk[off .. off + 30]
#@ ensures \forall i: int; (0 <= i and i < len(name)) ==> disk[off + i] == ord(name[i])
#@ ensures len(name) < 30 ==> disk[off + len(name)] == 0
def encode_name_field(disk: List[int], off: int, name: str) -> None:
    m = len(name)
    # ONE pass over the full 30-byte field (the faithful `_pad_name` blit): position i gets
    # the name byte if i < m, else 0 (null pad). A single loop avoids an inter-loop carry of
    # the tail-zero fact, so each invariant is a clean per-position byte equation.
    #@ loop invariant 0 <= i and i <= 30
    #@ loop invariant m == len(name)
    #@ loop invariant \forall j: int; (0 <= j and j < i and j < m) ==> disk[off + j] == ord(name[j])
    #@ loop invariant \forall j: int; (0 <= j and j < i and j >= m) ==> disk[off + j] == 0
    #@ loop variant 30 - i
    for i in range(30):
        if i < m:
            disk[off + i] = ord(name[i])
        else:
            disk[off + i] = 0


# The END-TO-END write rung: ENCODE a name into slot k's 30-byte name field (via the byte-only
# helper, so the string axiom never enters the blit loop), then conclude the abstract per-slot
# name decode equals `name`. The helper's byte postconditions establish the codec axiom's
# preconditions; the cited round-trip closes `field_to_str(disk, off, 30) == name`, and the
# bridge rewrites that to `slot_name(disk, blk, k) == name`. Both string axioms fire EXACTLY
# ONCE here (at the decode site, with the byte facts already in hand — the f2-composition
# shape that crosses O(1)), never per-iteration. This is the shape the os `_write_dir_entry`
# body would prove for its `slot_name(self.dir, blk, slot) == name` write-side ensures.
#@ requires blk >= 0 and blk < 256
#@ requires k >= 0 and k < 16
#@ requires len(name) <= 30
#@ requires \forall i: int; (0 <= i and i < len(name)) ==> ord(name[i]) != 0
#@ requires \valid(disk, blk * 512 + 32 * k + 2 + 30)
#@ assigns disk[blk * 512 + 32 * k + 2 .. blk * 512 + 32 * k + 2 + 30]
#@ ensures slot_name(disk, blk, k) == name
#@ proof rocq UnixFs.Dir.slot_name_byte_decode
#@ proof lean UnixFs.Dir.slot_name_byte_decode
#@ proof rocq UnixFs.Field.field_to_str_round_trip
#@ proof lean UnixFs.Field.field_to_str_round_trip
def write_name_field(disk: List[int], blk: int, k: int, name: str) -> None:
    off = blk * 512 + 32 * k + 2
    encode_name_field(disk, off, name)
    #@ assert field_to_str(disk, off, 30) == name
