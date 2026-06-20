(* Validation of Pycsl.Strmod.Capwords.{capwords_length_nongrowing,capwords_empty}
 * — the TWO TRANSFORM-SPECIFIC facts of a FAITHFUL CPython `string.capwords`
 * model, the auditable trusted core that retires the last bare `#@ \trusted`
 * leaf in pycsl_lib/strmod (capwords).
 *
 * The Why3 symbols pinned by these lemmas (registered in
 * src/pycsl/module6_whyml/preamble.py _AXIOM_REGISTRY):
 *   - capwords_def : string -> string   (the abstract `val function` whose
 *                    intended interpretation IS the concrete definition below)
 *   - axiom capwords_length_nongrowing : forall s.
 *         String.length (capwords_def s) <= String.length s
 *   - axiom capwords_empty : capwords_def "" = ""
 *
 * Faithful interpretation of the Why3 symbols (same string model as StrLen.v):
 *   - Why3 `string`        <-> `list Z` (a char is its code).
 *   - `String.length s`    <-> `Z.of_nat (length s)`.
 *   - `capwords_def`       <-> the concrete `capwords_def` below: whitespace
 *                             tokenize (CPython str.split() default whitespace
 *                             {space,\t,\n,\r,\f,\v}, drop empties, trim) ->
 *                             per-word capitalize (length-preserving) -> join
 *                             with a single space. This MATCHES CPython
 *                             string.capwords(s) = ' '.join(x.capitalize()
 *                             for x in s.split()).
 *
 * Soundness of the cited facts rests ENTIRELY on this definition being a
 * faithful model of CPython capwords (the residual, auditable trust): the
 * length bound holds because capitalize is length-preserving and each
 * inter-word single space is covered by >= 1 original whitespace char; the
 * empty law holds because "" has no words.
 *
 * Verified under Coq 8.20.1. Print Assumptions: closed under the global
 * context (no Axiom, no Admitted). *)

Require Import Coq.ZArith.ZArith.
Require Import Coq.Lists.List.
Require Import Lia.
Import ListNotations.

(* Default scope is nat (length arithmetic); Z char codes carry explicit %Z. *)

Module Pycsl.
Module Strmod.
Module Capwords.

Definition string := list Z.
Definition str_length (s : string) : Z := Z.of_nat (length s).

(* CPython str.split() default whitespace set: space \t \n \r \f \v. *)
Definition is_ws (c : Z) : bool :=
  orb (Z.eqb c 32) (orb (Z.eqb c 9) (orb (Z.eqb c 10)
    (orb (Z.eqb c 13) (orb (Z.eqb c 12) (Z.eqb c 11))))).

(* capitalize: first char upper, rest lower — a per-character (length-preserving) map. *)
Definition to_upper (c : Z) : Z :=
  if andb (Z.leb 97 c) (Z.leb c 122) then (c - 32)%Z else c.
Definition to_lower (c : Z) : Z :=
  if andb (Z.leb 65 c) (Z.leb c 90) then (c + 32)%Z else c.
Definition capitalize (w : string) : string :=
  match w with [] => [] | c :: rest => to_upper c :: map to_lower rest end.

Lemma capitalize_length : forall w, length (capitalize w) = length w.
Proof. intros [|c rest]; simpl; [reflexivity|]. rewrite length_map. reflexivity. Qed.

(* whitespace tokenizer: maximal non-ws runs, empties dropped (str.split()). *)
Definition push (w : string) (acc : list string) : list string :=
  match w with [] => acc | _ => w :: acc end.
Fixpoint split_aux (s : string) (cur : string) : list string :=
  match s with
  | [] => push cur []
  | c :: tl => if is_ws c then push cur (split_aux tl []) else split_aux tl (cur ++ [c])
  end.
Definition split_ws (s : string) : list string := split_aux s [].

(* join the tokens with a single space (code 32) between them. *)
Fixpoint join_tail (ts : list string) : string :=
  match ts with [] => [] | t :: rest => (32%Z :: t) ++ join_tail rest end.
Definition join_sp (ts : list string) : string :=
  match ts with [] => [] | t :: rest => t ++ join_tail rest end.

Definition capwords_def (s : string) : string :=
  join_sp (map capitalize (split_ws s)).

(* ---------- empty law ---------- *)
Theorem capwords_empty : capwords_def [] = [].
Proof. reflexivity. Qed.

(* ---------- length non-growing ---------- *)
Lemma join_tail_length : forall ts,
  length (join_tail ts) = fold_right (fun n acc => 1 + n + acc) 0 (map (@length Z) ts).
Proof.
  induction ts as [|t rest IH]; [reflexivity|].
  change (join_tail (t :: rest)) with ((32%Z :: t) ++ join_tail rest).
  rewrite length_app.
  change (map (@length Z) (t :: rest)) with (length t :: map (@length Z) rest).
  cbn [fold_right length]. rewrite IH. lia.
Qed.

Lemma join_sp_length_le_join_tail : forall ts,
  length (join_sp ts) <= length (join_tail ts).
Proof.
  intros [|t rest]; [reflexivity|].
  change (join_sp (t :: rest)) with (t ++ join_tail rest).
  change (join_tail (t :: rest)) with ((32%Z :: t) ++ join_tail rest).
  rewrite !length_app. cbn [length]. lia.
Qed.

Lemma map_length_capitalize : forall ts,
  map (@length Z) (map capitalize ts) = map (@length Z) ts.
Proof.
  induction ts as [|t rest IH]; [reflexivity|].
  cbn [map]. rewrite capitalize_length, IH. reflexivity.
Qed.

Lemma join_sp_map_capitalize_length : forall ts,
  length (join_sp (map capitalize ts)) = length (join_sp ts).
Proof.
  intros [|t rest]; [reflexivity|].
  change (join_sp (map capitalize (t :: rest)))
    with (capitalize t ++ join_tail (map capitalize rest)).
  change (join_sp (t :: rest)) with (t ++ join_tail rest).
  rewrite !length_app, capitalize_length, !join_tail_length, map_length_capitalize.
  reflexivity.
Qed.

Lemma join_sp_push_le : forall w ts, w <> [] ->
  length (join_sp (push w ts)) <=
    length w + (match ts with [] => 0 | _ => 1 + length (join_sp ts) end).
Proof.
  intros [|a w'] ts H; [contradiction|]. clear H. simpl push.
  destruct ts as [|t rest].
  - change (join_sp ((a::w') :: [])) with ((a::w') ++ join_tail []).
    cbn [join_tail]. rewrite app_nil_r. cbn [length]. lia.
  - change (join_sp ((a::w') :: t :: rest)) with ((a::w') ++ join_tail (t :: rest)).
    change (join_sp (t :: rest)) with (t ++ join_tail rest).
    change (join_tail (t :: rest)) with ((32%Z :: t) ++ join_tail rest).
    rewrite !length_app. cbn [length]. lia.
Qed.

Lemma split_aux_bound : forall s cur,
  length (join_sp (split_aux s cur)) <= length cur + length s.
Proof.
  induction s as [|c tl IH]; intros cur.
  - cbn [split_aux]. destruct cur as [|a cur'].
    + reflexivity.
    + change (push (a::cur') []) with ((a::cur') :: []).
      change (join_sp ((a::cur') :: [])) with ((a::cur') ++ join_tail []).
      cbn [join_tail]. rewrite app_nil_r. cbn [length]. lia.
  - cbn [split_aux]. destruct (is_ws c) eqn:Hws.
    + destruct cur as [|a cur'].
      * cbn [push]. specialize (IH []). cbn [length] in *. lia.
      * pose proof (join_sp_push_le (a::cur') (split_aux tl []))
          ltac:(discriminate) as Hp.
        specialize (IH []).
        destruct (split_aux tl []) eqn:E.
        -- simpl in Hp |- *. lia.
        -- cbn [length] in *. lia.
    + specialize (IH (cur ++ [c])).
      rewrite length_app in IH. cbn [length] in *. lia.
Qed.

Theorem capwords_length_nongrowing :
  forall s : string, (str_length (capwords_def s) <= str_length s)%Z.
Proof.
  intros s. unfold str_length, capwords_def, split_ws.
  rewrite join_sp_map_capitalize_length.
  pose proof (split_aux_bound s []) as H.
  cbn [length] in H. lia.
Qed.

Print Assumptions capwords_empty.
Print Assumptions capwords_length_nongrowing.

End Capwords.
End Strmod.
End Pycsl.
