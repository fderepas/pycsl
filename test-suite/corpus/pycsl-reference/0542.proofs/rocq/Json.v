Require Import ZArith.
Module Pycsl. Module Reference. Module Json.

Inductive json : Type :=
  | JNull : json
  | JInt : Z -> json
  | JPair : json -> json -> json.

Fixpoint mirror (j: json) : json :=
  match j with
  | JNull => JNull
  | JInt n => JInt n
  | JPair a b => JPair (mirror b) (mirror a)
  end.

(* Inductive property over a recursive datatype, by structural induction. *)
Theorem mirror_involution : forall j, mirror (mirror j) = j.
Proof.
  induction j; simpl.
  - reflexivity.
  - reflexivity.
  - rewrite IHj1, IHj2. reflexivity.
Qed.

End Json. End Reference. End Pycsl.
