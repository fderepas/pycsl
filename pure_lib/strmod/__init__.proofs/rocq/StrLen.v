(* Validation of Pycsl.Strmod.StrLen.length_nonneg — the STRING-UNIVERSAL
 * length-non-negativity fact that pins every "result is a string" leaf in
 * pure_lib/strmod (template_substitute / template_safe_substitute /
 * _format_field_nonempty / Template.substitute / Template.safe_substitute /
 * Formatter.format).
 *
 * The Why3 axiom is
 *
 *     forall s : string. String.length s >= 0
 *
 * i.e. EVERY string — whatever transform produced it — has non-negative length.
 * This is true of an ARBITRARY result string, so it can be proved as a generic
 * lemma about the abstract string type without defining any transform. The
 * strmod leaves are abstract `val`s whose sole sound `ensures` is exactly this
 * instance (`\str_length(\result) >= 0`); citing this cross-validated lemma
 * replaces the bare reviewer-`\trusted` with a named, proof-assistant-anchored
 * fact (the auditable trusted core), shrinking the TCB.
 *
 * Faithful interpretation of the Why3 symbols (the cross-validation contract,
 * same model as ../../../../test-suite/corpus/pycsl-reference/0708.proofs):
 *   - Why3 `string`         <-> `list Z` (a char is its code; no range bound
 *                               is needed for a pure length fact).
 *   - `String.length s`     <-> `Z.of_nat (length s)` — the int length of the
 *                               char list. `Z.of_nat _` is non-negative by
 *                               construction, which is the whole content of the
 *                               fact: length is a count, counts are >= 0.
 *   - `>=` (Why3 int order)  <-> `Z.ge`.
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom (closed under the global
 * context). *)

Require Import Coq.ZArith.ZArith.
Require Import Coq.Lists.List.
Require Import Lia.
Import ListNotations.
Open Scope Z_scope.

Module Pycsl.
Module Strmod.
Module StrLen.

(* A Why3 `string` is modelled as its list of character codes. *)
Definition string := list Z.

(* `String.length s` (Why3 int) is the int count of characters. *)
Definition str_length (s : string) : Z := Z.of_nat (length s).

(* The universal fact: the length of ANY string is non-negative. True of an
   arbitrary result string regardless of the transform that produced it. *)
Theorem length_nonneg :
  forall s : string, str_length s >= 0.
Proof.
  intros s. unfold str_length. lia.
Qed.

Print Assumptions length_nonneg.

End StrLen.
End Strmod.
End Pycsl.
