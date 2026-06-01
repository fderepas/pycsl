(* unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v
 *
 * Coq proofs of theorems cited by `#@ proof rocq` directives in
 * ../../UnixInodeFileSystem.py.
 *
 * Trust anchor for WhyML axioms PyCSL cannot discharge directly —
 * notably bitwise-AND postconditions where Z3 times out (~3.4B steps
 * observed on `(x >> y) & 1 ∈ {0, 1}`).
 *
 * Verified under Coq 8.20.1. No `Admitted`, no `Axiom`. *)

Require Import Coq.ZArith.ZArith.
Require Import Coq.ZArith.Zdiv.
Require Import Coq.Lists.List.
Require Import Lia.

Import ListNotations.
Open Scope Z_scope.

Module UnixFs.
Module Bitmap.

(* The load-bearing fact for `_get_bitmap`:
 *
 *   return (self.disk[byte_pos] >> bit_pos) & 1
 *
 * Postcondition: \result >= 0 and \result < 2.
 *
 * Z3 cannot dispatch this in 30s (3.4B steps observed) because integer
 * bitwise-AND requires reasoning over the bit-representation modulo 2.
 * Coq has it directly from `Z.land` semantics.
 *
 * The companion `#@ proof rocq UnixFs.Bitmap.bit_and_one_in_zero_one`
 * directive in UnixInodeFileSystem.py turns this Coq theorem into a
 * Why3 axiom that the SMT solver consumes in 0 steps. *)
Theorem bit_and_one_in_zero_one :
  forall n : Z, 0 <= Z.land n 1 < 2.
Proof.
  intros n.
  (* Key identity: `1 = Z.ones 1`, so `Z.land n 1 = Z.land n (Z.ones 1)`.
   * Then `Z.land_ones n 1 (0 <= 1)` gives `Z.land n (Z.ones 1) = n mod 2^1`.
   * And `2^1 = 2`, so `Z.land n 1 = n mod 2 ∈ [0, 2)` by `Z.mod_pos_bound`. *)
  assert (Hones : Z.ones 1 = 1) by reflexivity.
  assert (Hpow  : 2 ^ 1 = 2) by reflexivity.
  pose proof (Z.land_ones n 1 ltac:(lia)) as Hland.
  rewrite Hones in Hland.
  rewrite Hpow in Hland.
  rewrite Hland.
  apply Z.mod_pos_bound. lia.
Qed.

End Bitmap.

(* UnixFs.Struct — `struct.pack` / `struct.unpack` round-trip per format.
 *
 * The companion `#@ proof rocq UnixFs.Struct.<slot_id>.round_trip`
 * directive imports the round-trip theorem as a Why3 axiom
 * constraining the abstract `val function struct_pack_<id>` /
 * `val function struct_unpack_<id>` symbols emitted by Module6.
 *
 * The witness implementations below SATISFY the axiom — meaning the
 * axiom is consistent (some concrete pack/unpack exists that obeys
 * round-trip).  PyCSL leaves the WhyML symbols abstract, so the
 * axiom is the only operational fact the SMT solver sees.
 *
 * Format slot_ids follow `struct_format.StructFormat.slot_id()`:
 *   - `i1a1` ≡ one int + one bytes        (e.g. `>H30s`)
 *   - `i18`  ≡ eighteen ints              (e.g. `>IHHHHHII10Ixx`)
 *
 * We pick the simplest concrete witnesses so round-trip closes by
 * `reflexivity` — the format-string argument is irrelevant in the
 * witness (it's only used at the bit-level encoding layer which
 * PyCSL doesn't model). *)
Module Struct.

(* slot_id = i1a1 — corresponds to `>H30s` (one uint16 + 30-byte bytes).
 *
 * Witness:
 *   pack   fmt x0 x1   = [x0] ++ x1            (* x0 head, then the byte run *)
 *   unpack fmt data    = (default+head, rest)   where decomposition is
 *                                               by destructuring on data
 *
 * Round-trip: unpack (pack x0 x1) = (x0, x1)  — closes by `reflexivity`. *)
Module Fmt_i1a1.

  Definition pack (_fmt: Z) (x0: Z) (x1: list Z) : list Z :=
    x0 :: x1.

  Definition unpack (_fmt: Z) (data: list Z) : (Z * list Z) :=
    match data with
    | h :: rest => (h, rest)
    | []        => (0, [])
    end.

  Theorem round_trip :
    forall fmt x0 x1, unpack fmt (pack fmt x0 x1) = (x0, x1).
  Proof.
    intros fmt x0 x1. unfold pack, unpack. reflexivity.
  Qed.

End Fmt_i1a1.

(* slot_id = i2 — corresponds to `>HH` (two uint16). Witness lifts
 * (x0, x1) to a 2-element list. Round-trip closes by `reflexivity`. *)
Module Fmt_i2.

  Definition pack (_fmt: Z) (x0 x1: Z) : list Z := [x0; x1].

  Definition unpack (_fmt: Z) (data: list Z) : (Z * Z) :=
    match data with
    | x0 :: x1 :: _ => (x0, x1)
    | _ => (0, 0)
    end.

  Theorem round_trip :
    forall fmt x0 x1, unpack fmt (pack fmt x0 x1) = (x0, x1).
  Proof.
    intros. unfold pack, unpack. reflexivity.
  Qed.

End Fmt_i2.

(* slot_id = i18 — corresponds to `>IHHHHHII10Ixx` (18 ints in a 64-byte block).
 *
 * Witness: pack consumes its 18 int arguments to a length-18 list;
 * unpack returns that list back. Round-trip closes by `reflexivity`. *)
Module Fmt_i18.

  Definition pack (_fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9
                        x10 x11 x12 x13 x14 x15 x16 x17 : Z) : list Z :=
    [x0; x1; x2; x3; x4; x5; x6; x7; x8;
     x9; x10; x11; x12; x13; x14; x15; x16; x17].

  Definition unpack (_fmt: Z) (data: list Z) :
      (Z * Z * Z * Z * Z * Z * Z * Z * Z *
       Z * Z * Z * Z * Z * Z * Z * Z * Z) :=
    match data with
    | x0 :: x1 :: x2 :: x3 :: x4 :: x5 :: x6 :: x7 :: x8 ::
      x9 :: x10 :: x11 :: x12 :: x13 :: x14 :: x15 :: x16 :: x17 :: _ =>
        (x0, x1, x2, x3, x4, x5, x6, x7, x8,
         x9, x10, x11, x12, x13, x14, x15, x16, x17)
    | _ => (0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0)
    end.

  Theorem round_trip :
    forall fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9
               x10 x11 x12 x13 x14 x15 x16 x17,
      unpack fmt (pack fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9
                           x10 x11 x12 x13 x14 x15 x16 x17)
      = (x0, x1, x2, x3, x4, x5, x6, x7, x8,
         x9, x10, x11, x12, x13, x14, x15, x16, x17).
  Proof.
    intros. unfold pack, unpack. reflexivity.
  Qed.

End Fmt_i18.

End Struct.

End UnixFs.
