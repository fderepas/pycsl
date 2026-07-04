(* Cross-validated proofs for src/pycsl_lib/csys/__init__.py
   #@ proof rocq Pycsl.Csys.Colorsys.{sat_bound,hue_bound}
   These anchor the WhyML axioms in Module6 _AXIOM_REGISTRY that discharge the
   nonlinear integer-division bounds SMT times out on when de-trusting rgb_to_hsv.
   Division is Coq Z.div (floor); for a positive divisor it agrees with Why3's
   int.EuclideanDivision.div, and every hypothesis here has a positive divisor. *)
Require Import ZArith.
Require Import Lia.
Open Scope Z_scope.

Module Pycsl.
Module Csys.
Module Colorsys.

(* sat_bound: HSV saturation (diff*1000)//mx <= 1000 since diff <= mx. *)
Theorem sat_bound : forall d m : Z,
  0 <= d -> d <= m -> m > 0 -> (d * 1000) / m <= 1000.
Proof.
  intros d m Hd Hdm Hm.
  apply Z.le_trans with ((m * 1000) / m).
  - apply Z.div_le_mono; [ lia | nia ].
  - rewrite Z.mul_comm. rewrite Z.div_mul by lia. lia.
Qed.

(* hue_bound: hue offset (n*1000)//(6*d) in [-167,167] for |n| <= d, d > 0. *)
Theorem hue_bound : forall n d : Z,
  d > 0 -> (0 - d) <= n -> n <= d ->
  (0 - 167) <= (n * 1000) / (6 * d) /\ (n * 1000) / (6 * d) <= 167.
Proof.
  intros n d Hd Hlo Hhi.
  assert (H6 : 6 * d > 0) by lia.
  pose proof (Z.div_mod (n * 1000) (6 * d) ltac:(lia)) as Hdm.
  pose proof (Z.mod_pos_bound (n * 1000) (6 * d) ltac:(lia)) as Hmb.
  set (q := (n * 1000) / (6 * d)) in *.
  set (r := (n * 1000) mod (6 * d)) in *.
  split; nia.
Qed.

End Colorsys.
End Csys.
End Pycsl.
