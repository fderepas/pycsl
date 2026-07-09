(* Phase2c_PyValDict.v — certificate for the wall-plan-v2 concrete-map encoding.

   WALL-PLAN v2, Phase 1 (generic-dict-str-any-2-plan.md §1 D1–D3, §2 E4,
   §3 F4, §4).  This file is the axiom-free Rocq certificate co-landing with
   the WhyML `pydict`/`pyval`/`irkey`/`doc` theory promoted into the emitter
   preamble (`module6_whyml/preamble.py::_emit_pydict_theory`).  It certifies —
   against pure inductive datatypes, NO axiom — exactly the constructs the
   Phase-0 spike (`test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw`)
   proved on both SMT provers, so the value shape lands with a proof rather
   than a trusted assumption (the tier-3 coupling rule, cf. Phase2b_RecordVal.v):

     D1  `pyval`/`pydict` — strictly-positive nested inductive universal value;
         `get`/`mem_key` structural lookups; the concrete-lookup laws.
     D2  `irkey` interned keys + the string<->key boundary bijection
         (computable, no axiom — R-B: constructors, not strings).
     D3  `size` termination measure + the sub-term size lemma pack (induction).
     E4  `wf_ir` well-formedness predicate + the compositionality (binds-projection)
         lemma the unguarded-read VC discharges from.
     F4  `doc` document ADT + `render` monoid laws (R-C).

   The `Print Assumptions` block at the bottom is the make-or-break ledger
   check: every result must be "Closed under the global context" (NO axiom),
   so the 3-axiom trust ledger (alt_ergo_correct, trusted_contracts_axiom,
   why3_implements_wp_w) is UNCHANGED — this file adds none.

   Nothing here is `Admitted`.  Build: part of `make` (see `_CoqProject`). *)

Require Import ZArith String List Bool Lia.
Require Import Coq.Numbers.DecimalString Coq.Numbers.DecimalZ.
Import ListNotations.
Local Open Scope string_scope.

(* ===================================================================== *)
(* D2 — R-B: interned IR keys.  A finite schema-known enum; key equality  *)
(*      and disequality are pure constructor reasoning (no string theory  *)
(*      in any walker VC).  `K_dyn s` is the fallback for a genuinely      *)
(*      computed key (rare in Module 6).                                   *)
(* ===================================================================== *)

Inductive irkey : Type :=
  | K_type | K_left | K_right | K_op | K_z
  | K_value | K_target | K_body | K_orelse | K_func | K_name
  | K_dyn (s : string).

(* Boolean equality — decidable, computable (constructor reasoning). *)
Definition irkey_eqb (a b : irkey) : bool :=
  match a, b with
  | K_type, K_type | K_left, K_left | K_right, K_right | K_op, K_op
  | K_z, K_z | K_value, K_value | K_target, K_target | K_body, K_body
  | K_orelse, K_orelse | K_func, K_func | K_name, K_name => true
  | K_dyn s1, K_dyn s2 => String.eqb s1 s2
  | _, _ => false
  end.

Lemma irkey_eqb_refl : forall k, irkey_eqb k k = true.
Proof. destruct k; simpl; try reflexivity. apply String.eqb_refl. Qed.

Lemma irkey_eqb_eq : forall a b, irkey_eqb a b = true -> a = b.
Proof.
  destruct a; destruct b; simpl; intro H; try discriminate; try reflexivity.
  apply String.eqb_eq in H; subst; reflexivity.
Qed.

(* The reserved (named, nullary) key names, and the boundary bijection. *)
Definition reserved (s : string) : bool :=
  String.eqb s "type"  || String.eqb s "left"  || String.eqb s "right" ||
  String.eqb s "op"    || String.eqb s "z"     || String.eqb s "value" ||
  String.eqb s "target"|| String.eqb s "body"  || String.eqb s "orelse"||
  String.eqb s "func"  || String.eqb s "name".

Definition string_of_key (k : irkey) : string :=
  match k with
  | K_type => "type"   | K_left => "left"   | K_right => "right"
  | K_op => "op"       | K_z => "z"         | K_value => "value"
  | K_target => "target" | K_body => "body" | K_orelse => "orelse"
  | K_func => "func"   | K_name => "name"   | K_dyn s => s
  end.

Definition key_of_string (s : string) : irkey :=
  if String.eqb s "type"   then K_type
  else if String.eqb s "left"   then K_left
  else if String.eqb s "right"  then K_right
  else if String.eqb s "op"     then K_op
  else if String.eqb s "z"      then K_z
  else if String.eqb s "value"  then K_value
  else if String.eqb s "target" then K_target
  else if String.eqb s "body"   then K_body
  else if String.eqb s "orelse" then K_orelse
  else if String.eqb s "func"   then K_func
  else if String.eqb s "name"   then K_name
  else K_dyn s.

(* A key is well-formed when a `K_dyn` payload is not a reserved name (the
   canonicalization Module 5 maintains: schema keys use nullary constructors). *)
Definition key_wf (k : irkey) : Prop :=
  match k with K_dyn s => reserved s = false | _ => True end.

(* R-B computable bijection: string_of_key then key_of_string round-trips on
   every well-formed key.  Proof by evaluation (the named keys) + the K_dyn
   guard.  NO axiom. *)
Theorem key_roundtrip : forall k, key_wf k -> key_of_string (string_of_key k) = k.
Proof.
  destruct k; intro Hwf; try reflexivity.
  (* only the K_dyn s case survives; reserved s = false forces the fall-through *)
  cbn [string_of_key]. unfold key_wf, reserved in Hwf. unfold key_of_string.
  repeat match goal with
         | H : _ || _ = false |- _ => apply orb_false_elim in H; destruct H
         end.
  repeat match goal with
         | H : String.eqb s _ = false |- _ => rewrite H
         end.
  reflexivity.
Qed.

(* string_of_key is injective on well-formed keys (distinctness pack — free from
   the datatype, plus the reserved-name guard for K_dyn). *)
Theorem string_of_key_inj :
  forall k1 k2, key_wf k1 -> key_wf k2 ->
    string_of_key k1 = string_of_key k2 -> k1 = k2.
Proof.
  intros k1 k2 H1 H2 Heq.
  rewrite <- (key_roundtrip k1 H1). rewrite <- (key_roundtrip k2 H2).
  rewrite Heq. reflexivity.
Qed.

(* ===================================================================== *)
(* D1 — R-A: the strictly-positive concrete universal value.  No arrow /   *)
(*      no map in any constructor (the fmap strict-positivity rejection is  *)
(*      structurally impossible).  `pydict` is a bespoke assoc-list keyed    *)
(*      by irkey, nested inductive with `pyval`.                            *)
(* ===================================================================== *)

Inductive pyval : Type :=
  | PInt  (n : Z)
  | PStr  (s : string)
  | PBool (b : bool)
  | PNone
  | PList (xs : list pyval)
  | PDict (d : pydict)
with pydict : Type :=
  | DNil
  | DCons (k : irkey) (v : pyval) (d : pydict).

(* get / mem_key : structural over the dict; key test is irkey_eqb (constructor
   (dis)equality for schema keys — the R-B payoff). *)
Fixpoint get (d : pydict) (k : irkey) : option pyval :=
  match d with
  | DNil => None
  | DCons k' v rest => if irkey_eqb k k' then Some v else get rest k
  end.

Fixpoint mem_key (d : pydict) (k : irkey) : bool :=
  match d with
  | DNil => false
  | DCons k' _ rest => irkey_eqb k k' || mem_key rest k
  end.

Definition binds (k : irkey) (v : pyval) (d : pydict) : Prop := get d k = Some v.

(* Concrete-lookup laws (D1): a hit reads the bound value, `get`/`mem` agree.
   These are the assoc-list map laws the fmap theory had to axiomatize. *)
Lemma get_hit_head : forall k v rest, get (DCons k v rest) k = Some v.
Proof. intros; simpl; rewrite irkey_eqb_refl; reflexivity. Qed.

Lemma get_some_mem : forall d k v, get d k = Some v -> mem_key d k = true.
Proof.
  induction d as [| k' v' rest IH]; intros k v H; simpl in *.
  - discriminate.
  - destruct (irkey_eqb k k') eqn:E; simpl.
    + reflexivity.
    + rewrite (IH k v H); reflexivity.
Qed.

(* ===================================================================== *)
(* D3 — the `size` termination measure + the sub-term size lemma pack.     *)
(*      +1 per cons cell (list AND dict), so the HEAD recursion strictly    *)
(*      decreases even for a singleton (the spike's crux fix).  `size` uses  *)
(*      a nested `fix` over `list pyval` (Coq accepts this positively).     *)
(* ===================================================================== *)

Fixpoint size (v : pyval) : nat :=
  match v with
  | PInt _ | PStr _ | PBool _ | PNone => 1
  | PList xs =>
      1 + (fix size_list (l : list pyval) : nat :=
             match l with
             | [] => 0
             | h :: t => 1 + size h + size_list t
             end) xs
  | PDict d => 1 + size_dict d
  end
with size_dict (d : pydict) : nat :=
  match d with
  | DNil => 0
  | DCons _ v rest => 1 + size v + size_dict rest
  end.

(* size_list as a standalone definition matching the nested fix above. *)
Fixpoint size_list (l : list pyval) : nat :=
  match l with
  | [] => 0
  | h :: t => 1 + size h + size_list t
  end.

Lemma size_list_eq : forall xs, size (PList xs) = 1 + size_list xs.
Proof. intro xs; induction xs as [| h t IH]; simpl; reflexivity. Qed.

(* size_pos: every value has strictly positive size (each arm is `S _`). *)
Theorem size_pos : forall v, 0 < size v.
Proof. destruct v; simpl; apply Nat.lt_0_succ. Qed.

Theorem size_dict_nonneg : forall d, 0 <= size_dict d.
Proof. intro d; apply Nat.le_0_l. Qed.

(* size_dict_mem (the plan's sub-term law): a value bound in a dict is strictly
   smaller than the dict it lives in.  Proof by induction on the dict. *)
Theorem size_dict_mem :
  forall d k v, binds k v d -> size v < size (PDict d).
Proof.
  unfold binds. induction d as [| k' v' rest IH]; intros k v H; simpl in *.
  - discriminate.
  - destruct (irkey_eqb k k') eqn:E.
    + injection H; intro; subst v'. lia.
    + specialize (IH k v H). simpl in IH. lia.
Qed.

(* size_list_mem: a list element is strictly smaller than its container. *)
Theorem size_list_mem :
  forall xs x, In x xs -> size x < size (PList xs).
Proof.
  intros xs x Hin. rewrite size_list_eq.
  induction xs as [| h t IH]; simpl in *.
  - contradiction.
  - destruct Hin as [He | Ht].
    + subst h. lia.
    + specialize (IH Ht). lia.
Qed.

(* ===================================================================== *)
(* E4 — `wf_ir` well-formedness + the compositionality (binds-projection)  *)
(*      lemma the unguarded-read VC discharges from.  `wf_val` is the       *)
(*      per-key expected-shape predicate (here a representative: string     *)
(*      keys carry `PStr`); the generator (`wf_ir_gen.py`) emits the full   *)
(*      per-(shape,key) table from `ir_schema.py`.                          *)
(* ===================================================================== *)

(* Representative per-key value typing: the schema string-valued keys carry a
   PStr payload.  (The emitter's generated predicate refines this per shape.) *)
Definition wf_val (k : irkey) (v : pyval) : Prop :=
  match k with
  | K_op | K_type | K_target | K_func | K_name =>
      match v with PStr _ => True | _ => False end
  | _ => True
  end.

Fixpoint wf_dict (d : pydict) : Prop :=
  match d with
  | DNil => True
  | DCons k v rest => wf_val k v /\ wf_dict rest
  end.

Definition wf_ir (v : pyval) : Prop :=
  match v with PDict d => wf_dict d | _ => True end.

(* Compositionality: a well-formed dict, projected at any bound key, yields a
   value satisfying that key's typing.  This is E4's `wf_ir (PDict d) /\
   binds k v d ==> wf_val k v` — the fact the unguarded read leans on. *)
Theorem wf_ir_binds :
  forall d k v, wf_dict d -> binds k v d -> wf_val k v.
Proof.
  unfold binds. induction d as [| k' v' rest IH]; intros k v Hwf Hget; simpl in *.
  - discriminate.
  - destruct Hwf as [Hhead Htail].
    destruct (irkey_eqb k k') eqn:E.
    + injection Hget; intro; subst v'.
      apply irkey_eqb_eq in E; subst k'. exact Hhead.
    + apply (IH k v Htail Hget).
Qed.

(* Consequence used by E4 at a PStr-expecting read: a well-formed BinOp-shaped
   node projected at `op` yields a PStr, so the projection precondition
   `is_PStr (get n K_op)` is discharged from `wf_ir node`. *)
Corollary wf_ir_op_is_str :
  forall d v, wf_dict d -> binds K_op v d -> exists s, v = PStr s.
Proof.
  intros d v Hwf Hb. pose proof (wf_ir_binds d K_op v Hwf Hb) as Hv.
  simpl in Hv. destruct v; try contradiction. exists s; reflexivity.
Qed.

(* ===================================================================== *)
(* F4 — the document ADT `doc` + `render` monoid laws (R-C).  Walker        *)
(*      methods build `doc`; only `render` touches strings, and its         *)
(*      associativity / unit laws justify the emitter's f-string ->         *)
(*      DCat-chain rewrite.  DInt renders through a total decimal encoding.  *)
(* ===================================================================== *)

Inductive doc : Type :=
  | DText (s : string)
  | DInt  (n : Z)
  | DCat  (a b : doc)
  | DDoNil.

Definition string_of_Z (z : Z) : string :=
  NilZero.string_of_int (Z.to_int z).

(* string append is a monoid — proven locally (stdlib name varies by version). *)
Lemma str_app_assoc : forall a b c, (a ++ b) ++ c = a ++ (b ++ c).
Proof. induction a as [| ch a IH]; intros b c; simpl; [reflexivity | rewrite IH; reflexivity]. Qed.

Lemma str_app_nil_r : forall a, a ++ "" = a.
Proof. induction a as [| ch a IH]; simpl; [reflexivity | rewrite IH; reflexivity]. Qed.

Fixpoint render (d : doc) : string :=
  match d with
  | DText s => s
  | DInt n  => string_of_Z n
  | DCat a b => render a ++ render b
  | DDoNil  => ""
  end.

(* render laws — the monoid structure `render` transports DCat into ++. *)
Theorem render_text : forall s, render (DText s) = s.
Proof. reflexivity. Qed.

Theorem render_nil : render DDoNil = "".
Proof. reflexivity. Qed.

Theorem render_cat : forall a b, render (DCat a b) = render a ++ render b.
Proof. reflexivity. Qed.

Theorem render_cat_assoc :
  forall a b c, render (DCat (DCat a b) c) = render (DCat a (DCat b c)).
Proof. intros; simpl; rewrite str_app_assoc; reflexivity. Qed.

Theorem render_nil_left : forall a, render (DCat DDoNil a) = render a.
Proof. reflexivity. Qed.

Theorem render_nil_right : forall a, render (DCat a DDoNil) = render a.
Proof. intro a; simpl. rewrite str_app_nil_r. reflexivity. Qed.

(* ===================================================================== *)
(* T3 — ir-traversal-residual: the string-keyed symbol table `sdict`        *)
(*      (env-threaded fold, plan §5).  A SECOND, deliberately-boring        *)
(*      datatype whose keys are RUNTIME strings (NOT interned irkey), with  *)
(*      an option-valued `slookup` — the 2nd/last co-landed certificate.    *)
(*      Ordinary inductive datatype + a total structural Fixpoint; the      *)
(*      lemma pack is one induction each.  NO axiom.  Two facts keep the    *)
(*      computed-key read in the solved discipline: (a) `String.eqb`'s      *)
(*      result is program code no VC constrains (insight C); (b) the read   *)
(*      returns `option` with an explicit `None` arm (defensive            *)
(*      totalization).                                                      *)
(* ===================================================================== *)

Inductive sdict : Type :=
  | SNil
  | SCons (k : string) (v : pyval) (rest : sdict).

Fixpoint slookup (k : string) (s : sdict) : option pyval :=
  match s with
  | SNil => None
  | SCons k' v rest => if String.eqb k k' then Some v else slookup k rest
  end.

(* smem : membership by key (the boolean companion, mirroring mem_key). *)
Fixpoint smem (k : string) (s : sdict) : bool :=
  match s with
  | SNil => false
  | SCons k' _ rest => String.eqb k k' || smem k rest
  end.

(* slookup termination/totality is structural (a total Fixpoint) — Rocq
   accepts it by construction.  We certify the OPTION-SHAPE / IN-BOUNDS pack. *)

(* (1) head hit — a matching head key reads its bound value. *)
Lemma slookup_hit_head :
  forall k k' v rest, String.eqb k k' = true ->
    slookup k (SCons k' v rest) = Some v.
Proof. intros k k' v rest H; simpl; rewrite H; reflexivity. Qed.

(* (2) soundness — a `Some` hit implies membership (mirrors get_some_mem). *)
Lemma slookup_some_smem :
  forall s k v, slookup k s = Some v -> smem k s = true.
Proof.
  induction s as [| k' v' rest IH]; intros k v H; simpl in *.
  - discriminate.
  - destruct (String.eqb k k') eqn:E; simpl.
    + reflexivity.
    + rewrite (IH k v H); reflexivity.
Qed.

(* sdict_size : total node count of a symbol table (for the in-bounds law). *)
Fixpoint sdict_size (s : sdict) : nat :=
  match s with
  | SNil => 0
  | SCons _ v rest => 1 + size v + sdict_size rest
  end.

(* (3) in-bounds / sub-term — a value found by slookup is strictly smaller
   than the table it lives in (mirrors size_dict_mem for the pydict case). *)
Theorem size_slookup_mem :
  forall s k v, slookup k s = Some v -> size v < sdict_size s.
Proof.
  induction s as [| k' v' rest IH]; intros k v H; simpl in *.
  - discriminate.
  - destruct (String.eqb k k') eqn:E.
    + injection H; intro; subst v'. lia.
    + specialize (IH k v H). lia.
Qed.

(* ===================================================================== *)
(* VERDICT — assumption audit.  Every result Closed under the global       *)
(*    context (NO axiom): the 3-axiom trust ledger is intact, +0.          *)
(* ===================================================================== *)

Print Assumptions key_roundtrip.
Print Assumptions string_of_key_inj.
Print Assumptions irkey_eqb_eq.
Print Assumptions get_hit_head.
Print Assumptions get_some_mem.
Print Assumptions size_pos.
Print Assumptions size_dict_mem.
Print Assumptions size_list_mem.
Print Assumptions wf_ir_binds.
Print Assumptions wf_ir_op_is_str.
Print Assumptions render_cat_assoc.
Print Assumptions render_nil_left.
Print Assumptions render_nil_right.
Print Assumptions slookup_hit_head.
Print Assumptions slookup_some_smem.
Print Assumptions size_slookup_mem.
