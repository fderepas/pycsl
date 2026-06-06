(*
 * Golden test fixture for rocq2pycsl — strings.
 *
 * `concat_length s t` returns `\str_length(s) + \str_length(t)`.
 * The theorem expresses this via `String.length` and `String.append`
 * (`s ++ t`), exercising the StrLength / StrConcat IR nodes.
 *)

Require Import String.

Definition concat_length (s t : string) : nat :=
  String.length s + String.length t.

Theorem concat_length_correct : forall (s t : string),
  concat_length s t = String.length s + String.length t.
Admitted.
