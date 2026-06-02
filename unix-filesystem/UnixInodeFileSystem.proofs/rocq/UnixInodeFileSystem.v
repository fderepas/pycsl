(* unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v
 *
 * Coq proofs of theorems cited by `#@ proof rocq` directives in
 * ../../UnixInodeFileSystem.py.
 *
 * Trust anchor for WhyML axioms PyCSL cannot discharge directly —
 * notably bitwise-AND postconditions where Z3 times out.
 *
 * The pack/unpack/bit_and functions are defined at TOP LEVEL with the
 * SAME symbol names as the Module 6 `_AXIOM_REGISTRY` (`bit_and`,
 * `struct_pack_iN`, `struct_unpack_iN`) so the proof-statement
 * cross-check (bin/check-proof-crosscheck.sh) sees the same symbols in
 * all three sources (Rocq, Lean, registry). The cited theorems live in
 * the `UnixFs.{Bitmap,Struct.iN}` namespaces.
 *
 * Verified under Coq 8.20.1. No `Admitted`, no `Axiom`. *)

(* `Require Export` + `Global Open Scope` so that a module which merely
 * `Require Import`s this file (e.g. the cross-check's `Check` companion)
 * inherits the ZArith / list notations and Z scope — otherwise the
 * extracted statement prints un-elaborated (`BinInt.Z.le`, `BinNums.Zpos
 * BinNums.xH`) instead of `<=` / `1`, and the cross-check can't match it. *)
Require Export Coq.ZArith.ZArith.
Require Export Coq.Lists.List.
Require Import Coq.ZArith.Zdiv.
Require Import Lia.

Export ListNotations.
Global Open Scope Z_scope.

(* --- Top-level witness functions (names match the registry symbols) --- *)

Definition bit_and (x y : Z) : Z := Z.land x y.

Definition struct_pack_i1a1 (_fmt : Z) (x0 : Z) (x1 : list Z) : list Z :=
  x0 :: x1.
Definition struct_unpack_i1a1 (_fmt : Z) (data : list Z) : (Z * list Z) :=
  match data with
  | h :: rest => (h, rest)
  | []        => (0, [])
  end.

Definition struct_pack_i2 (_fmt x0 x1 : Z) : list Z := [x0; x1].
Definition struct_unpack_i2 (_fmt : Z) (data : list Z) : (Z * Z) :=
  match data with
  | x0 :: x1 :: _ => (x0, x1)
  | _ => (0, 0)
  end.

Definition struct_pack_i18 (_fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9
                                 x10 x11 x12 x13 x14 x15 x16 x17 : Z) : list Z :=
  [x0; x1; x2; x3; x4; x5; x6; x7; x8;
   x9; x10; x11; x12; x13; x14; x15; x16; x17].
Definition struct_unpack_i18 (_fmt : Z) (data : list Z) :
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

(* --- Cited theorems (qualnames match the `#@ proof rocq` directives) --- *)

Module UnixFs.
Module Bitmap.

(* `(self.disk[byte_pos] >> bit_pos) & 1 ∈ {0,1}` — Z3 times out; Coq
 * dispatches via `Z.land` semantics. Stated with `bit_and` so the
 * registry/Lean/Rocq symbols agree. *)
Theorem bit_and_one_in_zero_one :
  forall n : Z, 0 <= bit_and n 1 /\ bit_and n 1 < 2.
Proof.
  intros n. unfold bit_and.
  assert (Hones : Z.ones 1 = 1) by reflexivity.
  assert (Hpow  : 2 ^ 1 = 2) by reflexivity.
  pose proof (Z.land_ones n 1 ltac:(lia)) as Hland.
  rewrite Hones in Hland. rewrite Hpow in Hland. rewrite Hland.
  pose proof (Z.mod_pos_bound n 2 ltac:(lia)) as Hb. lia.
Qed.

End Bitmap.

Module Struct.

Module i1a1.
  (* >H30s — one int + one byte run. *)
  Theorem round_trip :
    forall fmt x0 x1,
      struct_unpack_i1a1 fmt (struct_pack_i1a1 fmt x0 x1) = (x0, x1).
  Proof.
    intros fmt x0 x1. unfold struct_pack_i1a1, struct_unpack_i1a1.
    reflexivity.
  Qed.
End i1a1.

Module i2.
  (* >HH — two ints. *)
  Theorem round_trip :
    forall fmt x0 x1,
      struct_unpack_i2 fmt (struct_pack_i2 fmt x0 x1) = (x0, x1).
  Proof.
    intros. unfold struct_pack_i2, struct_unpack_i2. reflexivity.
  Qed.
End i2.

Module i18.
  (* >IHHHHHII10Ixx — eighteen ints in a 64-byte inode block. *)
  Theorem round_trip :
    forall fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9
               x10 x11 x12 x13 x14 x15 x16 x17,
      struct_unpack_i18 fmt (struct_pack_i18 fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9
                                 x10 x11 x12 x13 x14 x15 x16 x17)
      = (x0, x1, x2, x3, x4, x5, x6, x7, x8,
         x9, x10, x11, x12, x13, x14, x15, x16, x17).
  Proof.
    intros. unfold struct_pack_i18, struct_unpack_i18. reflexivity.
  Qed.
End i18.

End Struct.

End UnixFs.
