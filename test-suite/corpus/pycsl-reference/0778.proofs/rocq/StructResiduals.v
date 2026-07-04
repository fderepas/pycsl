(* cleared-pack RESIDUALS — cross-validated Rocq proofs for the faithful struct
   family widened to a per-field width/signedness tag: multi-slot unsigned
   (u16u32), signed singles (i16/i32/i64, two's complement), signed multi
   (i32i32), and fixed-bytes (s4).  pack/unpack are DEFINED as the real big-endian
   base-256 byte serialisation (with struct's mod-256 truncation and two's-
   complement sign folding), so every round-trip is a GENUINE theorem, not a
   reflexivity witness over uninterpreted symbols.  Division is Coq Z.div (floor);
   for the positive divisors here it agrees with Why3 int.EuclideanDivision.div. *)
Require Import ZArith Lia List.
Import ListNotations.
Open Scope Z_scope.

Module Pycsl.
Module Struct.
Module Std.

(* ===== unsigned single-field big-endian base-256 codecs ===== *)
Definition pk16 (x : Z) : list Z := [ (x / 256) mod 256 ; x mod 256 ].
Definition up16 (d : list Z) : Z := nth 0 d 0 * 256 + nth 1 d 0.

Definition pk32 (x : Z) : list Z :=
  [ (x / 16777216) mod 256 ; (x / 65536) mod 256 ;
    (x / 256) mod 256 ; x mod 256 ].
Definition up32 (d : list Z) : Z :=
  nth 0 d 0 * 16777216 + nth 1 d 0 * 65536 + nth 2 d 0 * 256 + nth 3 d 0.

Definition pk64 (x : Z) : list Z :=
  [ (x / 72057594037927936) mod 256 ; (x / 281474976710656) mod 256 ;
    (x / 1099511627776) mod 256 ; (x / 4294967296) mod 256 ;
    (x / 16777216) mod 256 ; (x / 65536) mod 256 ;
    (x / 256) mod 256 ; x mod 256 ].
Definition up64 (d : list Z) : Z :=
  nth 0 d 0 * 72057594037927936 + nth 1 d 0 * 281474976710656 +
  nth 2 d 0 * 1099511627776 + nth 3 d 0 * 4294967296 +
  nth 4 d 0 * 16777216 + nth 5 d 0 * 65536 + nth 6 d 0 * 256 + nth 7 d 0.

Lemma urt16 : forall x, 0 <= x -> x < 65536 -> up16 (pk16 x) = x.
Proof.
  intros x H0 H1. unfold up16, pk16. simpl.
  assert (Hq : 0 <= x / 256 < 256).
  { split. apply Z.div_pos; lia. apply Z.div_lt_upper_bound; lia. }
  rewrite (Z.mod_small (x / 256) 256) by lia.
  rewrite (Z.mul_comm (x / 256) 256).
  symmetry. apply (Z.div_mod x 256). lia.
Qed.

Lemma urt32 : forall x, 0 <= x -> x < 4294967296 -> up32 (pk32 x) = x.
Proof.
  intros x H0 H1. unfold up32, pk32. simpl.
  pose proof (Z.div_mod x 256 ltac:(lia)) as E0.
  pose proof (Z.div_mod (x / 256) 256 ltac:(lia)) as E1.
  pose proof (Z.div_mod (x / 65536) 256 ltac:(lia)) as E2.
  assert (D1 : x / 256 / 256 = x / 65536) by (rewrite Zdiv_Zdiv by lia; reflexivity).
  assert (D2 : x / 65536 / 256 = x / 16777216) by (rewrite Zdiv_Zdiv by lia; reflexivity).
  assert (Hhi : 0 <= x / 16777216 < 256).
  { split. apply Z.div_pos; lia. apply Z.div_lt_upper_bound; lia. }
  rewrite (Z.mod_small (x / 16777216) 256) by lia.
  rewrite D1 in E1. rewrite D2 in E2. lia.
Qed.

Lemma urt64 : forall x, 0 <= x -> x < 18446744073709551616 -> up64 (pk64 x) = x.
Proof.
  intros x H0 H1. unfold up64, pk64. simpl.
  pose proof (Z.div_mod x 256 ltac:(lia)) as E0.
  pose proof (Z.div_mod (x / 256) 256 ltac:(lia)) as E1.
  pose proof (Z.div_mod (x / 65536) 256 ltac:(lia)) as E2.
  pose proof (Z.div_mod (x / 16777216) 256 ltac:(lia)) as E3.
  pose proof (Z.div_mod (x / 4294967296) 256 ltac:(lia)) as E4.
  pose proof (Z.div_mod (x / 1099511627776) 256 ltac:(lia)) as E5.
  pose proof (Z.div_mod (x / 281474976710656) 256 ltac:(lia)) as E6.
  assert (D1 : x / 256 / 256 = x / 65536) by (rewrite Zdiv_Zdiv by lia; reflexivity).
  assert (D2 : x / 65536 / 256 = x / 16777216) by (rewrite Zdiv_Zdiv by lia; reflexivity).
  assert (D3 : x / 16777216 / 256 = x / 4294967296) by (rewrite Zdiv_Zdiv by lia; reflexivity).
  assert (D4 : x / 4294967296 / 256 = x / 1099511627776) by (rewrite Zdiv_Zdiv by lia; reflexivity).
  assert (D5 : x / 1099511627776 / 256 = x / 281474976710656) by (rewrite Zdiv_Zdiv by lia; reflexivity).
  assert (D6 : x / 281474976710656 / 256 = x / 72057594037927936) by (rewrite Zdiv_Zdiv by lia; reflexivity).
  assert (Hhi : 0 <= x / 72057594037927936 < 256).
  { split. apply Z.div_pos; lia. apply Z.div_lt_upper_bound; lia. }
  rewrite (Z.mod_small (x / 72057594037927936) 256) by lia.
  rewrite D1 in E1. rewrite D2 in E2. rewrite D3 in E3.
  rewrite D4 in E4. rewrite D5 in E5. rewrite D6 in E6. lia.
Qed.

(* ===== signed single-field codecs (two's complement) =====
   packI x = pkU (x mod M);  unpackI d = let u := upU d in
   if M/2 <= u then u - M else u.  Round-trip for -M/2 <= x < M/2. *)
Definition pk_i16 (x : Z) : list Z := pk16 (x mod 65536).
Definition up_i16 (d : list Z) : Z := let u := up16 d in if 32768 <=? u then u - 65536 else u.
Definition pk_i32 (x : Z) : list Z := pk32 (x mod 4294967296).
Definition up_i32 (d : list Z) : Z := let u := up32 d in if 2147483648 <=? u then u - 4294967296 else u.
Definition pk_i64 (x : Z) : list Z := pk64 (x mod 18446744073709551616).
Definition up_i64 (d : list Z) : Z := let u := up64 d in if 9223372036854775808 <=? u then u - 18446744073709551616 else u.

Lemma srt16 : forall x, -32768 <= x -> x < 32768 -> up_i16 (pk_i16 x) = x.
Proof.
  intros x H0 H1. unfold up_i16, pk_i16.
  assert (Hm : 0 <= x mod 65536 < 65536) by (apply Z.mod_pos_bound; lia).
  rewrite urt16 by lia.
  pose proof (Z.div_mod x 65536 ltac:(lia)) as E.
  destruct (32768 <=? x mod 65536) eqn:Hc;
    [ apply Z.leb_le in Hc | apply Z.leb_gt in Hc ]; lia.
Qed.

Lemma srt32 : forall x, -2147483648 <= x -> x < 2147483648 -> up_i32 (pk_i32 x) = x.
Proof.
  intros x H0 H1. unfold up_i32, pk_i32.
  assert (Hm : 0 <= x mod 4294967296 < 4294967296) by (apply Z.mod_pos_bound; lia).
  rewrite urt32 by lia.
  pose proof (Z.div_mod x 4294967296 ltac:(lia)) as E.
  destruct (2147483648 <=? x mod 4294967296) eqn:Hc;
    [ apply Z.leb_le in Hc | apply Z.leb_gt in Hc ]; lia.
Qed.

Lemma srt64 : forall x, -9223372036854775808 <= x -> x < 9223372036854775808 -> up_i64 (pk_i64 x) = x.
Proof.
  intros x H0 H1. unfold up_i64, pk_i64.
  assert (Hm : 0 <= x mod 18446744073709551616 < 18446744073709551616) by (apply Z.mod_pos_bound; lia).
  rewrite urt64 by lia.
  pose proof (Z.div_mod x 18446744073709551616 ltac:(lia)) as E.
  destruct (9223372036854775808 <=? x mod 18446744073709551616) eqn:Hc;
    [ apply Z.leb_le in Hc | apply Z.leb_gt in Hc ]; lia.
Qed.

(* ===== multi-slot: fields occupy disjoint byte ranges (concatenation) ===== *)
Definition pk_u16u32 (x0 x1 : Z) : list Z := pk16 x0 ++ pk32 x1.
Definition up_u16u32 (d : list Z) : Z * Z :=
  (up16 [nth 0 d 0; nth 1 d 0], up32 [nth 2 d 0; nth 3 d 0; nth 4 d 0; nth 5 d 0]).

Theorem round_trip_u16u32 : forall x0 x1,
  0 <= x0 -> x0 < 65536 -> 0 <= x1 -> x1 < 4294967296 ->
  up_u16u32 (pk_u16u32 x0 x1) = (x0, x1).
Proof.
  intros x0 x1 A B C D. unfold up_u16u32, pk_u16u32, pk16, pk32. simpl.
  f_equal.
  - change (up16 [(x0/256) mod 256; x0 mod 256] = x0). apply urt16; lia.
  - change (up32 [(x1/16777216) mod 256; (x1/65536) mod 256; (x1/256) mod 256; x1 mod 256] = x1).
    apply urt32; lia.
Qed.

Definition pk_i32i32 (x0 x1 : Z) : list Z := pk_i32 x0 ++ pk_i32 x1.
Definition up_i32i32 (d : list Z) : Z * Z :=
  (up_i32 [nth 0 d 0; nth 1 d 0; nth 2 d 0; nth 3 d 0],
   up_i32 [nth 4 d 0; nth 5 d 0; nth 6 d 0; nth 7 d 0]).

Theorem round_trip_i32i32 : forall x0 x1,
  -2147483648 <= x0 -> x0 < 2147483648 -> -2147483648 <= x1 -> x1 < 2147483648 ->
  up_i32i32 (pk_i32i32 x0 x1) = (x0, x1).
Proof.
  intros x0 x1 A B C D. unfold up_i32i32, pk_i32i32, pk_i32, pk32. simpl.
  f_equal.
  - change (up_i32 (pk32 (x0 mod 4294967296)) = x0). apply srt32; lia.
  - change (up_i32 (pk32 (x1 mod 4294967296)) = x1). apply srt32; lia.
Qed.

(* named single-field round-trips for citation *)
Theorem round_trip_i16 : forall x, -32768 <= x -> x < 32768 -> up_i16 (pk_i16 x) = x.
Proof. apply srt16. Qed.
Theorem round_trip_i32 : forall x, -2147483648 <= x -> x < 2147483648 -> up_i32 (pk_i32 x) = x.
Proof. apply srt32. Qed.
Theorem round_trip_i64 : forall x, -9223372036854775808 <= x -> x < 9223372036854775808 -> up_i64 (pk_i64 x) = x.
Proof. apply srt64. Qed.

(* ===== fixed-bytes s4: identity under the length guard =====
   struct.pack('4s', d) truncates d to 4 bytes (and null-pads if shorter); the
   round-trip guard `length d = 4` pins it to the identity. *)
Definition pk_s4 (d : list Z) : list Z := firstn 4 d.
Definition up_s4 (d : list Z) : list Z := d.

Theorem round_trip_s4 : forall d, Z.of_nat (List.length d) = 4 -> up_s4 (pk_s4 d) = d.
Proof.
  intros d Hlen. unfold up_s4, pk_s4. apply firstn_all2. lia.
Qed.

(* ===== size laws ===== *)
Theorem size_u16u32 : forall x0 x1, Z.of_nat (List.length (pk_u16u32 x0 x1)) = 6.
Proof. intros. reflexivity. Qed.
Theorem size_i16 : forall x, Z.of_nat (List.length (pk_i16 x)) = 2.
Proof. intros. reflexivity. Qed.
Theorem size_i32 : forall x, Z.of_nat (List.length (pk_i32 x)) = 4.
Proof. intros. reflexivity. Qed.
Theorem size_i64 : forall x, Z.of_nat (List.length (pk_i64 x)) = 8.
Proof. intros. reflexivity. Qed.
Theorem size_i32i32 : forall x0 x1, Z.of_nat (List.length (pk_i32i32 x0 x1)) = 8.
Proof. intros. reflexivity. Qed.
Theorem size_s4 : forall d, Z.of_nat (List.length d) = 4 -> Z.of_nat (List.length (pk_s4 d)) = 4.
Proof.
  intros d Hlen. unfold pk_s4. rewrite firstn_length_le by lia. reflexivity.
Qed.

(* ===== guard-necessity counterexamples: one step out of range breaks it ===== *)
Theorem guard_necessity_u16u32 : up_u16u32 (pk_u16u32 65536 0) = (0, 0) /\ (65536 <> 0).
Proof. split; [ reflexivity | lia ]. Qed.
Theorem guard_necessity_i16 : up_i16 (pk_i16 32768) = -32768 /\ (32768 <> -32768).
Proof. split; [ reflexivity | lia ]. Qed.

End Std.
End Struct.
End Pycsl.
