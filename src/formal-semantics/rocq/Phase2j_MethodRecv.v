(* Phase2j_MethodRecv.v — axiom-free CERT-FEASIBILITY SPIKE for the emit_ir
   Call-receiver value-model extension (self-tcb-reduction Layer-2 wall).

   Models the ADDITIVE receiver-carrying method-call ctor
     type emit_ir = ... | IrMethodCall emit_ir string emit_ir int
   (receiver, func, arg0, arity) — parallel to `IrCall string emit_ir int`,
   exactly the IrCallKw precedent — plus the total `receiver_of` accessor and
   the extended `size` measure that COUNTS the receiver sub-term.

   The spike certifies, against a pure strictly-positive inductive with NO
   axiom, exactly what the emitter relies on:
     (a) the receiver is a strictly-positive recursive emit_ir occurrence — the
         `Inductive` is accepted and `emit_ir_rect` exists (the WhyML structural
         variant is well-founded);
     (b) size counts BOTH sub-terms → the receiver child is STRICTLY smaller
         (a recursive receiver-descending fold terminates);
     (c) receiver_of is TOTAL + faithful: a method call reads back its real
         receiver; a non-method-call reads the sentinel (real discrimination);
         the EVIL TWIN (wrong receiver) is provably UNprovable (non-vacuity);
     (d) kind_of/is_call agree and the ctor is injective on the receiver slot. *)

Require Import ZArith String List Bool Lia.
Import ListNotations.
Open Scope string_scope.
Local Open Scope Z_scope.

(* A REPRESENTATIVE fragment of the emit_ir sum: the existing IrCall + a couple
   of leaf/recursive ctors + the NEW IrMethodCall.  (The real type has ~120
   ctors; well-foundedness/totality is compositional per-ctor, so the fragment
   is faithful for the receiver-extension question.) *)
Inductive emit_ir : Type :=
  | IrVar        (name : string)
  | IrStr        (s : string)
  | IrNum        (v : Z)
  | IrOther      (s : string)                                   (* the sentinel *)
  | IrAttr       (obj : emit_ir) (field : string)
  | IrCall       (func : string) (arg0 : emit_ir) (arity : Z)
  | IrMethodCall (recv : emit_ir) (func : string) (arg0 : emit_ir) (arity : Z).

(* --- (a) structural recursion principle EXISTS (well-founded inductive) --- *)
Definition emit_ir_recursion_exists := emit_ir_rect.
Check emit_ir_rect.

(* --- the extended size measure: IrMethodCall counts recv AND arg0 --- *)
Fixpoint size (e : emit_ir) : Z :=
  match e with
  | IrVar _              => 1
  | IrStr _              => 1
  | IrNum _              => 1
  | IrOther _            => 1
  | IrAttr o _           => 1 + size o
  | IrCall _ a _         => 1 + size a
  | IrMethodCall r _ a _ => 1 + size r + size a
  end.

Theorem size_pos : forall e, size e >= 1.
Proof. induction e; cbn [size]; lia. Qed.

(* --- (b) the receiver child is STRICTLY smaller (fold terminates) --- *)
Theorem recv_size_lt : forall r f a n, size r < size (IrMethodCall r f a n).
Proof. intros; cbn [size]; pose proof (size_pos a); pose proof (size_pos r); lia. Qed.
Theorem mcall_arg0_size_lt : forall r f a n, size a < size (IrMethodCall r f a n).
Proof. intros; cbn [size]; pose proof (size_pos a); pose proof (size_pos r); lia. Qed.

(* --- (c) receiver_of is TOTAL + faithful --- *)
Definition receiver_of (e : emit_ir) : emit_ir :=
  match e with
  | IrMethodCall r _ _ _ => r
  | _                    => IrOther ""
  end.

Theorem receiver_of_faithful : forall r f a n, receiver_of (IrMethodCall r f a n) = r.
Proof. reflexivity. Qed.
Theorem receiver_of_call_sentinel : forall f a n, receiver_of (IrCall f a n) = IrOther "".
Proof. reflexivity. Qed.
Theorem receiver_of_var_sentinel : forall x, receiver_of (IrVar x) = IrOther "".
Proof. reflexivity. Qed.

(* EVIL TWIN: a WRONG receiver is provably UNprovable (non-vacuity). *)
Theorem receiver_of_evil : forall f a n,
  IrVar "x" <> IrVar "wrong" ->
  receiver_of (IrMethodCall (IrVar "x") f a n) <> IrVar "wrong".
Proof. intros f a n H C; cbn [receiver_of] in C; exact (H C). Qed.

(* --- (d) kind_of / is_call agree + injectivity on the receiver slot --- *)
Definition kind_of (e : emit_ir) : string :=
  match e with
  | IrCall _ _ _         => "Call"
  | IrMethodCall _ _ _ _ => "Call"
  | IrAttr _ _           => "Attribute"
  | _                    => "Other"
  end.

Definition is_call (e : emit_ir) : bool :=
  match e with
  | IrCall _ _ _         => true
  | IrMethodCall _ _ _ _ => true
  | _                    => false
  end.

Theorem kind_mcall : forall r f a n, kind_of (IrMethodCall r f a n) = "Call".
Proof. reflexivity. Qed.
Theorem iscall_mcall : forall r f a n, is_call (IrMethodCall r f a n) = true.
Proof. reflexivity. Qed.
Theorem iscall_var : forall x, is_call (IrVar x) = false.
Proof. reflexivity. Qed.

Theorem mcall_inj : forall r1 f1 a1 n1 r2 f2 a2 n2,
  IrMethodCall r1 f1 a1 n1 = IrMethodCall r2 f2 a2 n2 ->
  r1 = r2 /\ f1 = f2 /\ a1 = a2 /\ n1 = n2.
Proof. intros; inversion H; repeat split; reflexivity. Qed.

(* A method call is NEVER a bare IrCall (the receiver-dropping node) — the
   distinction the extension exists to preserve. *)
Theorem mcall_neq_call : forall r f1 a1 n1 f2 a2 n2,
  IrMethodCall r f1 a1 n1 <> IrCall f2 a2 n2.
Proof. intros; discriminate. Qed.

(* ===================================================================== *)
(* Trust check — every result Closed under the global context (NO axiom). *)
(* ===================================================================== *)
Print Assumptions size_pos.
Print Assumptions recv_size_lt.
Print Assumptions mcall_arg0_size_lt.
Print Assumptions receiver_of_faithful.
Print Assumptions receiver_of_call_sentinel.
Print Assumptions receiver_of_evil.
Print Assumptions kind_mcall.
Print Assumptions iscall_mcall.
Print Assumptions mcall_inj.
Print Assumptions mcall_neq_call.
