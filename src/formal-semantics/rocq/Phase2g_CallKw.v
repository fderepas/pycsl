(* Phase2g_CallKw.v — axiom-free certificate for the `emit_ir` Call-internals value
   model (self-tcb-reduction, Tier-5 value-model wall, J1).

   CO-LANDING COUPLING (the tier-3 rule, cf. Phase2e_PyAstStmt.v / Phase2f_PyVal.v):
   the WhyML keyword-node theory promoted into the emitter preamble
   (`module6_whyml/preamble.py::_emit_exprir_theory`, the standalone `kwval` /
   `keyword` / `keyword_list` types + the `IrCallKw` ctor + its projectors, gated on
   `_uses_call_kw`) is a NEW value shape — the faithful carrier for a Python Call
   node's `keywords` list, with the Name/Attribute distinction the bare-string callee
   currently COLLAPSES — so it lands with a proof, not a trusted assumption.  The
   Gate-R oracle (`getting-better/callinternals-oracle.mlw`, Z3-Valid, axiom-free)
   fixed the shape; this file certifies, against pure inductive datatypes with NO
   axiom, exactly what the emitter relies on:

     (a) `keyword_list` is a well-formed inductive: a BESPOKE cons-list
         (KWNil / KWCons), NOT `seq` — the strictly-positive shape Why3 accepts (the
         `seq` recursion is Why3-rejected).  `kwval` is a LEAF-string variant
         (KwName / KwAttr), so it carries no emit_ir and keyword_list stays standalone
         (the composition probe showed folding it into the `with irlist` mutual block
         hits a termination-measure wall);
     (b) the measure `kwlist_size` is well-founded — `kwlist_size l >= 0` and the tail
         of a cons is STRICTLY shorter, so any structural fold over the keyword list
         (the `for kw in call.keywords` iteration) terminates;
     (c) the value carriers are OBSERVABLE + DISTINCT — `KwName` / `KwAttr` are
         injective and `KwName s <> KwAttr t`: the ast.Name(`.id`) vs
         ast.Attribute(`.attr`) distinction is NEVER collapsed (the whole point of the
         model — the bare string erased it);
     (d) the make-or-break bound-EXTRACTION is faithful: `extract_bound` (the WhyML
         driver's logic image) iterates the keyword list, matches `kw.arg = "bound"`,
         and projects the value node's `.id` / `.attr` FAITHFULLY — the string
         VARIABLE arm reads back as `Some v` (no int-hash / int-erasure); a non-bound
         keyword list reads `None` (real discrimination); the multi-element case
         actually iterates; and the EVIL TWIN — a WRONG projected value — is provably
         UNprovable (non-vacuity).

   `kwval` HAS decidable equality (both arms are strings) — unlike `pyval` — but the
   emitter never needs it (the extraction is a key-guarded projection), so it is not
   claimed; only the injectivity/distinctness laws it actually depends on are.

   The `Print Assumptions` block at the bottom is the trust check: every result must
   be `Closed under the global context` (NO axiom) so the 3-axiom trust ledger
   (`proof_axiom_allowlist.py`) stays intact.  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2f_PyVal.v`). *)

Require Import ZArith String List Bool Lia.
Import ListNotations.
Open Scope string_scope.

Section CallKw.

Local Open Scope Z_scope.

(* ===================================================================== *)
(* 1. The keyword-node ADT — mirrors the WhyML                            *)
(*      type kwval = KwName string | KwAttr string                        *)
(*      type keyword = { kw_arg: string; kw_value: kwval }                *)
(*      type keyword_list = KWNil | KWCons keyword keyword_list.          *)
(* ===================================================================== *)

(* kwval: KwName carries an ast.Name node's `.id`; KwAttr carries an
   ast.Attribute node's `.attr` — exactly the distinction emit_ir's bare-string
   callee COLLAPSES.  A LEAF variant: neither arm carries a keyword / keyword_list,
   so keyword_list is strictly positive and standalone. *)
Inductive kwval : Type :=
  | KwName (s : string)
  | KwAttr (s : string).

(* keyword: the arg-name + value node.  A record (the WhyML `{ kw_arg; kw_value }`). *)
Record keyword : Type := mkkw { kw_arg : string; kw_value : kwval }.

(* keyword_list: the BESPOKE cons-list (KWNil / KWCons), NOT `seq`. *)
Inductive keyword_list : Type :=
  | KWNil
  | KWCons (k : keyword) (t : keyword_list).

(* ===================================================================== *)
(* 2. (a)+(c) The kwval projectors + discriminants (the WhyML             *)
(*    is_kwname / kwname_id / is_kwattr / kwattr_of).  Total.             *)
(* ===================================================================== *)

Definition is_kwname (v : kwval) : bool :=
  match v with KwName _ => true | KwAttr _ => false end.

(* the guarded projectors: each reads its ctor's sole string (the "other" arm keeps
   the function total — the driver guards by is_kwname so only the intended arm fires). *)
Definition kwname_id (v : kwval) : string :=
  match v with KwName s => s | KwAttr s => s end.
Definition kwattr_of (v : kwval) : string :=
  match v with KwAttr s => s | KwName s => s end.

(* ===================================================================== *)
(* 3. (b) The keyword-list measure is well-founded.                       *)
(* ===================================================================== *)

Fixpoint kwlist_size (l : keyword_list) : Z :=
  match l with
  | KWNil        => 0
  | KWCons _ t   => 1 + kwlist_size t
  end.

Theorem kwlist_size_nonneg : forall l : keyword_list, kwlist_size l >= 0.
Proof. induction l as [| k t IH]; cbn [kwlist_size]; lia. Qed.

Theorem kwlist_size_nil : kwlist_size KWNil = 0.
Proof. reflexivity. Qed.
Theorem kwlist_size_cons : forall k t, kwlist_size (KWCons k t) = 1 + kwlist_size t.
Proof. reflexivity. Qed.

(* The TAIL of a cons is STRICTLY shorter — the termination witness for the
   `for kw in call.keywords` structural fold (the WhyML program `let rec` needs a
   `variant { kws }`; Why3 infers exactly this descent). *)
Theorem kwlist_tail_size_lt : forall k t, kwlist_size t < kwlist_size (KWCons k t).
Proof. intros k t; cbn [kwlist_size]; pose proof (kwlist_size_nonneg t); lia. Qed.

(* A non-empty keyword list is DISTINCT from the empty one (a captured list is
   OBSERVABLE, not KWNil-erased). *)
Theorem kwlist_empty_neq_cons : forall k t, KWNil <> KWCons k t.
Proof. intros k t C; discriminate. Qed.

(* ===================================================================== *)
(* 4. (c) The kwval carriers are OBSERVABLE + DISTINCT — the             *)
(*    Name(.id) vs Attribute(.attr) distinction is NEVER collapsed.       *)
(* ===================================================================== *)

Theorem kwname_inj : forall a b, KwName a = KwName b -> a = b.
Proof. intros a b H; inversion H; reflexivity. Qed.
Theorem kwattr_inj : forall a b, KwAttr a = KwAttr b -> a = b.
Proof. intros a b H; inversion H; reflexivity. Qed.

(* THE make-or-break distinctness: a Name node is NEVER an Attribute node — the two
   AST kinds are not collapsed to one string (what the bare-string callee did). *)
Theorem kwname_neq_kwattr : forall s t, KwName s <> KwAttr t.
Proof. intros s t C; discriminate. Qed.

(* the discriminant AGREES with the constructor (honest, not degenerate). *)
Theorem is_kwname_name : forall s, is_kwname (KwName s) = true.
Proof. reflexivity. Qed.
Theorem is_kwname_attr : forall s, is_kwname (KwAttr s) = false.
Proof. reflexivity. Qed.
(* each guarded projector reads its intended field. *)
Theorem kwname_id_name : forall s, kwname_id (KwName s) = s.
Proof. reflexivity. Qed.
Theorem kwattr_of_attr : forall s, kwattr_of (KwAttr s) = s.
Proof. reflexivity. Qed.

(* ===================================================================== *)
(* 5. (d) The bound-EXTRACTION is faithful — the make-or-break.           *)
(*    `extract_bound` is the WhyML driver's logic image: iterate the       *)
(*    keyword list, match kw.arg = "bound", project the value node.        *)
(* ===================================================================== *)

Fixpoint extract_bound (kws : keyword_list) : option string :=
  match kws with
  | KWNil        => None
  | KWCons k rest =>
      if string_dec (kw_arg k) "bound" then
        (if is_kwname (kw_value k)
         then Some (kwname_id (kw_value k))
         else Some (kwattr_of (kw_value k)))
      else extract_bound rest
  end.

(* G1 (the oracle's G1_name_projects): the Name arm — a `bound=` keyword whose value
   is an ast.Name projects `.id` FAITHFULLY.  The string VARIABLE v (not a ground
   constant) reads back as `Some v` — a genuine value-carrying proof, NO int-erasure. *)
Theorem extract_name_faithful : forall v : string,
  extract_bound (KWCons (mkkw "bound" (KwName v)) KWNil) = Some v.
Proof.
  intros v; cbn [extract_bound kw_arg kw_value is_kwname kwname_id].
  destruct (string_dec "bound" "bound") as [_|N]; [reflexivity | now contradiction N].
Qed.

(* G2 (G2_attr_projects): the Attribute arm — project `.attr` faithfully. *)
Theorem extract_attr_faithful : forall a : string,
  extract_bound (KWCons (mkkw "bound" (KwAttr a)) KWNil) = Some a.
Proof.
  intros a; cbn [extract_bound kw_arg kw_value is_kwname kwattr_of].
  destruct (string_dec "bound" "bound") as [_|N]; [reflexivity | now contradiction N].
Qed.

(* G3 (G3_no_bound_none): a keyword list with NO "bound" arg reads `None` — the
   driver genuinely discriminates on the arg name (not vacuous). *)
Theorem extract_no_bound_none : forall v : string,
  extract_bound (KWCons (mkkw "other" (KwName v)) KWNil) = None.
Proof.
  intros v; cbn [extract_bound kw_arg].
  destruct (string_dec "other" "bound") as [E|_]; [discriminate E | reflexivity].
Qed.

(* G4 (G4_iterate_finds): the for-loop ACTUALLY iterates — "bound" is found AFTER a
   non-bound head. *)
Theorem extract_iterate_finds : forall v a : string,
  extract_bound
    (KWCons (mkkw "notit" (KwAttr a))
      (KWCons (mkkw "bound" (KwName v)) KWNil)) = Some v.
Proof.
  intros v a; cbn [extract_bound kw_arg kw_value is_kwname kwname_id].
  destruct (string_dec "notit" "bound") as [E|_]; [discriminate E |].
  destruct (string_dec "bound" "bound") as [_|N]; [reflexivity | now contradiction N].
Qed.

(* G5 (G5_evil_wrong_value — the EVIL TWIN): a WRONG projected value is provably
   UNprovable.  When v <> "wrong", the extraction is NOT `Some "wrong"`.  An
   int-erased / vacuous lowering would let this false claim through — this is the
   non-vacuity witness. *)
Theorem extract_evil_wrong_value : forall v : string,
  v <> "wrong" ->
  extract_bound (KWCons (mkkw "bound" (KwName v)) KWNil) <> Some "wrong".
Proof.
  intros v H C. rewrite extract_name_faithful in C.
  apply H. inversion C. reflexivity.
Qed.

(* G6 (G6_concrete_discriminates): the model produces a SPECIFIC value distinguishable
   from a wrong constant (Valid non-vacuity). *)
Theorem extract_concrete_discriminates :
  extract_bound (KWCons (mkkw "bound" (KwName "aaa")) KWNil) = Some "aaa"
  /\ extract_bound (KWCons (mkkw "bound" (KwName "aaa")) KWNil) <> Some "bbb".
Proof.
  split.
  - apply extract_name_faithful.
  - rewrite extract_name_faithful. intro C. inversion C.
Qed.

End CallKw.

(* ===================================================================== *)
(* 6. VERDICT — assumption audit.  Every result must be `Closed under the  *)
(*    global context` (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions kwlist_size_nonneg.
Print Assumptions kwlist_size_nil.
Print Assumptions kwlist_size_cons.
Print Assumptions kwlist_tail_size_lt.
Print Assumptions kwlist_empty_neq_cons.
Print Assumptions kwname_inj.
Print Assumptions kwattr_inj.
Print Assumptions kwname_neq_kwattr.
Print Assumptions is_kwname_name.
Print Assumptions is_kwname_attr.
Print Assumptions kwname_id_name.
Print Assumptions kwattr_of_attr.
Print Assumptions extract_name_faithful.
Print Assumptions extract_attr_faithful.
Print Assumptions extract_no_bound_none.
Print Assumptions extract_iterate_finds.
Print Assumptions extract_evil_wrong_value.
Print Assumptions extract_concrete_discriminates.
