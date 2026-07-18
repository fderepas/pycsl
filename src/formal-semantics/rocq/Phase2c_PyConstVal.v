(* Phase2c_PyConstVal.v — axiom-free certificate for the `pyconst_val`
   value-variant ADT (self-tcb-reduction M5, B-bucket).

   CO-LANDING COUPLING (the tier-3 rule, cf. Phase2b_RecordVal.v /
   Phase2c_PyValDict.v): the WhyML `pyconst_val` theory promoted into the
   emitter preamble (`module6_whyml/preamble.py::_emit_exprir_theory`) is a NEW
   value shape — the discriminated union of the Python constant scalar kinds an
   `ast.Constant` node's `.value` field holds — so it must land with a proof,
   not a trusted assumption.  This file certifies, against pure inductive
   datatypes with NO axiom, exactly what the emitter's `_py_expr_constant`
   handler relies on when it lowers `expr.value is None` /
   `isinstance(expr.value, bool/str/int/bytes/complex)` / `expr.value is ...`:

     (a) the abstraction map `abs : pyscalar -> pyconst_val` (a Python constant
         scalar to its ADT variant) is TOTAL and INJECTIVE (hence injective per
         kind), and SURJECTIVE onto the ADT;
     (b) each `is_pv*` discriminant AGREES with the corresponding Python
         `isinstance` / `is None` / `is ...` test (`is_pvnone (abs s) =
         py_is_none s`, ...);
     (c) each `pv*_of` projector is EXACT on its own variant
         (`pvbool_of (PVBool b) = b`, ...), both directly and through `abs`.

   The WhyML `PVComplex` leaf carries a `real`; to keep this certificate
   axiom-free (Coq's `Reals` pulls in classical axioms) the complex payload is
   abstracted by a Section type variable `rho` — the structural facts (a)/(b)/(c)
   hold for ANY payload type, `real` included.  The abstract WhyML `val`s
   `bytes_content_comp` / `real_trunc` are NOT certified here: `real_trunc` is
   pinned by `ensures` to Why3's own stdlib `truncate` (no PyCSL axiom), and
   `bytes_content_comp`'s per-byte content law is an in-WhyML assumed spec whose
   non-vacuity rests on `IrNum` injectivity — neither is a `pyconst_val`
   soundness obligation.

   The `Print Assumptions` block at the bottom is the trust check: every result
   must be `Closed under the global context` (NO axiom) so the 3-axiom trust
   ledger (`proof_axiom_allowlist.py`) stays intact.  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2c_PyValDict.v`). *)

Require Import ZArith String List Bool.
Import ListNotations.

Section PyConstVal.

(* The WhyML `PVComplex real` payload, abstracted (see header). *)
Variable rho : Type.
Variable rho0 : rho.   (* the `0.0` default of the WhyML `pvreal_of` off-variant *)

(* ===================================================================== *)
(* 1. The value-variant ADT — mirrors the WhyML `type pyconst_val`.       *)
(* ===================================================================== *)

Inductive pyconst_val : Type :=
  | PVNone
  | PVBool (b : bool)
  | PVInt (n : Z)
  | PVStr (s : string)
  | PVBytes (bs : list Z)
  | PVComplex (r : rho)
  | PVEllipsis.

(* Discriminants — verbatim images of the WhyML `is_pv*` match bodies. *)
Definition is_pvnone (v : pyconst_val) : bool :=
  match v with PVNone => true | _ => false end.
Definition is_pvbool (v : pyconst_val) : bool :=
  match v with PVBool _ => true | _ => false end.
Definition is_pvint (v : pyconst_val) : bool :=
  match v with PVInt _ => true | _ => false end.
Definition is_pvstr (v : pyconst_val) : bool :=
  match v with PVStr _ => true | _ => false end.
Definition is_pvbytes (v : pyconst_val) : bool :=
  match v with PVBytes _ => true | _ => false end.
Definition is_pvcomplex (v : pyconst_val) : bool :=
  match v with PVComplex _ => true | _ => false end.
Definition is_pvellipsis (v : pyconst_val) : bool :=
  match v with PVEllipsis => true | _ => false end.

(* Total projectors — verbatim images of the WhyML `pv*_of`, SAME defaults. *)
Definition pvbool_of (v : pyconst_val) : bool :=
  match v with PVBool b => b | _ => false end.
Definition pvint_of (v : pyconst_val) : Z :=
  match v with PVInt n => n | _ => 0%Z end.
Definition pvstr_of (v : pyconst_val) : string :=
  match v with PVStr s => s | _ => EmptyString end.
Definition pvbytes_of (v : pyconst_val) : list Z :=
  match v with PVBytes bs => bs | _ => [] end.
Definition pvreal_of (v : pyconst_val) : rho :=
  match v with PVComplex r => r | _ => rho0 end.

(* ===================================================================== *)
(* 2. The Python constant-scalar world + its isinstance / is-None tests.   *)
(* ===================================================================== *)

Inductive pyscalar : Type :=
  | SNone
  | SBool (b : bool)
  | SInt (n : Z)
  | SStr (s : string)
  | SBytes (bs : list Z)
  | SComplex (r : rho)
  | SEllipsis.

(* Python's runtime type tests on a constant scalar. `SBool`/`SInt` are kept
   DISJOINT here (bool is modelled as its own kind) — matching the emitter's
   branch order, which tests `isinstance(x, bool)` before the int fall-through,
   so a Python bool never reaches the `PVInt` arm. *)
Definition py_is_none (s : pyscalar) : bool :=
  match s with SNone => true | _ => false end.
Definition py_is_bool (s : pyscalar) : bool :=
  match s with SBool _ => true | _ => false end.
Definition py_is_int (s : pyscalar) : bool :=
  match s with SInt _ => true | _ => false end.
Definition py_is_str (s : pyscalar) : bool :=
  match s with SStr _ => true | _ => false end.
Definition py_is_bytes (s : pyscalar) : bool :=
  match s with SBytes _ => true | _ => false end.
Definition py_is_complex (s : pyscalar) : bool :=
  match s with SComplex _ => true | _ => false end.
Definition py_is_ellipsis (s : pyscalar) : bool :=
  match s with SEllipsis => true | _ => false end.

(* The abstraction map: a Python constant scalar to its ADT variant. *)
Definition abs (s : pyscalar) : pyconst_val :=
  match s with
  | SNone      => PVNone
  | SBool b    => PVBool b
  | SInt n     => PVInt n
  | SStr s     => PVStr s
  | SBytes bs  => PVBytes bs
  | SComplex r => PVComplex r
  | SEllipsis  => PVEllipsis
  end.

(* ===================================================================== *)
(* 3. (a) `abs` is total + injective (per kind) + surjective.             *)
(* ===================================================================== *)

Theorem abs_injective : forall x y, abs x = abs y -> x = y.
Proof. intros [] []; simpl; congruence. Qed.

Theorem abs_surjective : forall v, exists s, abs s = v.
Proof.
  intros v; destruct v.
  - exists SNone; reflexivity.
  - exists (SBool b); reflexivity.
  - exists (SInt n); reflexivity.
  - exists (SStr s); reflexivity.
  - exists (SBytes bs); reflexivity.
  - exists (SComplex r); reflexivity.
  - exists SEllipsis; reflexivity.
Qed.

(* ===================================================================== *)
(* 4. (b) each `is_pv*` AGREES with the matching Python type test.        *)
(* ===================================================================== *)

Theorem is_pvnone_agree : forall s, is_pvnone (abs s) = py_is_none s.
Proof. intros []; reflexivity. Qed.
Theorem is_pvbool_agree : forall s, is_pvbool (abs s) = py_is_bool s.
Proof. intros []; reflexivity. Qed.
Theorem is_pvint_agree : forall s, is_pvint (abs s) = py_is_int s.
Proof. intros []; reflexivity. Qed.
Theorem is_pvstr_agree : forall s, is_pvstr (abs s) = py_is_str s.
Proof. intros []; reflexivity. Qed.
Theorem is_pvbytes_agree : forall s, is_pvbytes (abs s) = py_is_bytes s.
Proof. intros []; reflexivity. Qed.
Theorem is_pvcomplex_agree : forall s, is_pvcomplex (abs s) = py_is_complex s.
Proof. intros []; reflexivity. Qed.
Theorem is_pvellipsis_agree : forall s, is_pvellipsis (abs s) = py_is_ellipsis s.
Proof. intros []; reflexivity. Qed.

(* ===================================================================== *)
(* 5. (c) each `pv*_of` is EXACT on its own variant (direct + via `abs`). *)
(* ===================================================================== *)

Theorem pvbool_of_exact : forall b, pvbool_of (PVBool b) = b.
Proof. reflexivity. Qed.
Theorem pvint_of_exact : forall n, pvint_of (PVInt n) = n.
Proof. reflexivity. Qed.
Theorem pvstr_of_exact : forall s, pvstr_of (PVStr s) = s.
Proof. reflexivity. Qed.
Theorem pvbytes_of_exact : forall bs, pvbytes_of (PVBytes bs) = bs.
Proof. reflexivity. Qed.
Theorem pvreal_of_exact : forall r, pvreal_of (PVComplex r) = r.
Proof. reflexivity. Qed.

Theorem pvbool_of_abs : forall b, pvbool_of (abs (SBool b)) = b.
Proof. reflexivity. Qed.
Theorem pvint_of_abs : forall n, pvint_of (abs (SInt n)) = n.
Proof. reflexivity. Qed.
Theorem pvstr_of_abs : forall s, pvstr_of (abs (SStr s)) = s.
Proof. reflexivity. Qed.
Theorem pvbytes_of_abs : forall bs, pvbytes_of (abs (SBytes bs)) = bs.
Proof. reflexivity. Qed.
Theorem pvreal_of_abs : forall r, pvreal_of (abs (SComplex r)) = r.
Proof. reflexivity. Qed.

End PyConstVal.

(* ===================================================================== *)
(* 6. VERDICT — assumption audit.  Every result must be `Closed under the  *)
(*    global context` (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions abs_injective.
Print Assumptions abs_surjective.
Print Assumptions is_pvnone_agree.
Print Assumptions is_pvbool_agree.
Print Assumptions is_pvint_agree.
Print Assumptions is_pvstr_agree.
Print Assumptions is_pvbytes_agree.
Print Assumptions is_pvcomplex_agree.
Print Assumptions is_pvellipsis_agree.
Print Assumptions pvbool_of_exact.
Print Assumptions pvint_of_exact.
Print Assumptions pvstr_of_exact.
Print Assumptions pvbytes_of_exact.
Print Assumptions pvreal_of_exact.
Print Assumptions pvbool_of_abs.
Print Assumptions pvint_of_abs.
Print Assumptions pvstr_of_abs.
Print Assumptions pvbytes_of_abs.
Print Assumptions pvreal_of_abs.
