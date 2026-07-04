(* Cross-validated proofs for test-suite/corpus/pycsl-reference/0753.py
   #@ proof rocq Pycsl.Struct.Std.{round_trip_u16,round_trip_u32}
   Anchors the WhyML axioms in Module6 _AXIOM_REGISTRY that give the FAITHFUL,
   GUARDED round-trip for single-slot standard-size big-endian unsigned struct
   formats ('>H' = u16, '>I' = u32). pack/unpack are DEFINED here as the real
   byte serialisation (base-256 big-endian, with the mod-256 truncation that
   struct.pack applies) — so the round-trip is a genuine theorem, NOT a
   reflexivity witness over uninterpreted symbols. Division is Coq Z.div (floor);
   for the positive divisors here it agrees with Why3 int.EuclideanDivision.div. *)
Require Import ZArith Lia List.
Import ListNotations.
Open Scope Z_scope.

Module Pycsl.
Module Struct.
Module Std.

(* ---- uint16, big-endian '>H' ---- *)
Definition pack16 (x : Z) : list Z := [ (x / 256) mod 256 ; x mod 256 ].
Definition unpack16 (d : list Z) : Z := nth 0 d 0 * 256 + nth 1 d 0.

Theorem size_u16 : forall x : Z, Z.of_nat (List.length (pack16 x)) = 2.
Proof. intro x. reflexivity. Qed.

Theorem round_trip_u16 : forall x : Z,
  0 <= x -> x < 65536 -> unpack16 (pack16 x) = x.
Proof.
  intros x H0 H1. unfold unpack16, pack16. simpl.
  assert (Hq : 0 <= x / 256 < 256).
  { split. apply Z.div_pos; lia. apply Z.div_lt_upper_bound; lia. }
  rewrite (Z.mod_small (x / 256) 256) by lia.
  rewrite (Z.mul_comm (x / 256) 256).
  symmetry. apply (Z.div_mod x 256). lia.
Qed.

(* GUARD-NECESSITY: one step out of range the round-trip BREAKS. *)
Theorem guard_necessity_u16 : unpack16 (pack16 65536) = 0 /\ (65536 <> 0).
Proof. split; [ reflexivity | lia ]. Qed.

(* ---- uint32, big-endian '>I' ---- *)
Definition pack32 (x : Z) : list Z :=
  [ (x / 16777216) mod 256 ; (x / 65536) mod 256 ;
    (x / 256) mod 256 ; x mod 256 ].
Definition unpack32 (d : list Z) : Z :=
  nth 0 d 0 * 16777216 + nth 1 d 0 * 65536 + nth 2 d 0 * 256 + nth 3 d 0.

Theorem size_u32 : forall x : Z, Z.of_nat (List.length (pack32 x)) = 4.
Proof. intro x. reflexivity. Qed.

Theorem round_trip_u32 : forall x : Z,
  0 <= x -> x < 4294967296 -> unpack32 (pack32 x) = x.
Proof.
  intros x H0 H1. unfold unpack32, pack32. simpl.
  (* the four base-256 digits, telescoping via successive div/mod *)
  pose proof (Z.div_mod x 256 ltac:(lia)) as E0.
  pose proof (Z.div_mod (x / 256) 256 ltac:(lia)) as E1.
  pose proof (Z.div_mod (x / 65536) 256 ltac:(lia)) as E2.
  assert (D1 : x / 256 / 256 = x / 65536) by (rewrite Zdiv_Zdiv by lia; reflexivity).
  assert (D2 : x / 65536 / 256 = x / 16777216) by (rewrite Zdiv_Zdiv by lia; reflexivity).
  assert (Hhi : 0 <= x / 16777216 < 256).
  { split. apply Z.div_pos; lia. apply Z.div_lt_upper_bound; lia. }
  rewrite (Z.mod_small (x / 16777216) 256) by lia.
  rewrite D1 in E1. rewrite D2 in E2.
  lia.
Qed.

Theorem guard_necessity_u32 : unpack32 (pack32 4294967296) = 0 /\ (4294967296 <> 0).
Proof. split; [ reflexivity | lia ]. Qed.

End Std.
End Struct.
End Pycsl.
