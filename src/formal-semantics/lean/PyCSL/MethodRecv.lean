/-
  MethodRecv.lean — axiom-free CERT-FEASIBILITY SPIKE for the emit_ir
  Call-receiver value-model extension (self-tcb-reduction Layer-2 wall).
  The Lean twin of `rocq/Phase2j_MethodRecv.v`.

  Models the ADDITIVE receiver-carrying method-call ctor
    IrMethodCall (recv : EmitIr) (func : String) (arg0 : EmitIr) (arity : Int)
  parallel to `IrCall`, plus the total `receiverOf` accessor and the extended
  `size` measure counting the receiver sub-term.  Certified NO axiom:
    (a) receiver is a strictly-positive recursive occurrence (the recursor exists);
    (b) size counts BOTH sub-terms → the receiver child is STRICTLY smaller;
    (c) receiverOf is TOTAL + faithful; the EVIL TWIN is provably UNprovable;
    (d) kindOf/isCall agree + injectivity on the receiver slot.

  Verdict decided by `#print axioms`: only the 3 standard kernel axioms may
  appear (propext, Classical.choice, Quot.sound) — NO 4th, extension axiom.
-/

namespace MethodRecvCert

-- A representative fragment of the emit_ir sum + the NEW IrMethodCall.
inductive EmitIr where
  | IrVar        (name : String)
  | IrStr        (s : String)
  | IrNum        (v : Int)
  | IrOther      (s : String)                                   -- the sentinel
  | IrAttr       (obj : EmitIr) (field : String)
  | IrCall       (func : String) (arg0 : EmitIr) (arity : Int)
  | IrMethodCall (recv : EmitIr) (func : String) (arg0 : EmitIr) (arity : Int)

open EmitIr

-- the extended size measure: IrMethodCall counts recv AND arg0.
def size : EmitIr → Int
  | .IrVar _              => 1
  | .IrStr _              => 1
  | .IrNum _              => 1
  | .IrOther _            => 1
  | .IrAttr o _           => 1 + size o
  | .IrCall _ a _         => 1 + size a
  | .IrMethodCall r _ a _ => 1 + size r + size a

-- (a) size positivity (structural induction over the well-founded inductive).
theorem size_pos : ∀ e : EmitIr, size e ≥ 1
  | .IrVar _              => by simp [size]
  | .IrStr _              => by simp [size]
  | .IrNum _              => by simp [size]
  | .IrOther _            => by simp [size]
  | .IrAttr o _           => by have := size_pos o; simp [size]; omega
  | .IrCall _ a _         => by have := size_pos a; simp [size]; omega
  | .IrMethodCall r _ a _ => by
      have := size_pos r; have := size_pos a; simp [size]; omega

-- (b) the receiver child is STRICTLY smaller (a receiver-descending fold terminates).
theorem recv_size_lt (r : EmitIr) (f : String) (a : EmitIr) (n : Int) :
    size r < size (.IrMethodCall r f a n) := by
  have := size_pos r; have := size_pos a; simp [size]; omega
theorem mcall_arg0_size_lt (r : EmitIr) (f : String) (a : EmitIr) (n : Int) :
    size a < size (.IrMethodCall r f a n) := by
  have := size_pos r; have := size_pos a; simp [size]; omega

-- (c) receiverOf TOTAL + faithful.
def receiverOf (e : EmitIr) : EmitIr :=
  match e with
  | .IrMethodCall r _ _ _ => r
  | _                     => .IrOther ""

theorem receiverOf_faithful (r : EmitIr) (f : String) (a : EmitIr) (n : Int) :
    receiverOf (.IrMethodCall r f a n) = r := by simp [receiverOf]
theorem receiverOf_call_sentinel (f : String) (a : EmitIr) (n : Int) :
    receiverOf (.IrCall f a n) = .IrOther "" := by simp [receiverOf]
theorem receiverOf_var_sentinel (x : String) :
    receiverOf (.IrVar x) = .IrOther "" := by simp [receiverOf]

-- EVIL TWIN: a WRONG receiver is provably UNprovable (non-vacuity).
theorem receiverOf_evil (f : String) (a : EmitIr) (n : Int) :
    (EmitIr.IrVar "x") ≠ (EmitIr.IrVar "wrong") →
    receiverOf (.IrMethodCall (.IrVar "x") f a n) ≠ (.IrVar "wrong") := by
  intro h c; simp only [receiverOf] at c; exact h c

-- (d) kindOf / isCall agree + injectivity on the receiver slot.
def kindOf (e : EmitIr) : String :=
  match e with
  | .IrCall _ _ _         => "Call"
  | .IrMethodCall _ _ _ _ => "Call"
  | .IrAttr _ _           => "Attribute"
  | _                     => "Other"

def isCall (e : EmitIr) : Bool :=
  match e with
  | .IrCall _ _ _         => true
  | .IrMethodCall _ _ _ _ => true
  | _                     => false

theorem kind_mcall (r : EmitIr) (f : String) (a : EmitIr) (n : Int) :
    kindOf (.IrMethodCall r f a n) = "Call" := by simp [kindOf]
theorem iscall_mcall (r : EmitIr) (f : String) (a : EmitIr) (n : Int) :
    isCall (.IrMethodCall r f a n) = true := by simp [isCall]
theorem iscall_var (x : String) : isCall (.IrVar x) = false := by simp [isCall]

theorem mcall_inj (r1 : EmitIr) (f1 : String) (a1 : EmitIr) (n1 : Int)
    (r2 : EmitIr) (f2 : String) (a2 : EmitIr) (n2 : Int) :
    EmitIr.IrMethodCall r1 f1 a1 n1 = EmitIr.IrMethodCall r2 f2 a2 n2 →
    r1 = r2 ∧ f1 = f2 ∧ a1 = a2 ∧ n1 = n2 := by
  intro h; injection h with h1 h2 h3 h4; exact ⟨h1, h2, h3, h4⟩

-- A method call is NEVER a bare IrCall (the receiver-dropping node).
theorem mcall_neq_call (r : EmitIr) (f1 : String) (a1 : EmitIr) (n1 : Int)
    (f2 : String) (a2 : EmitIr) (n2 : Int) :
    EmitIr.IrMethodCall r f1 a1 n1 ≠ EmitIr.IrCall f2 a2 n2 := by
  intro c; injection c

end MethodRecvCert

#print axioms MethodRecvCert.size_pos
#print axioms MethodRecvCert.recv_size_lt
#print axioms MethodRecvCert.mcall_arg0_size_lt
#print axioms MethodRecvCert.receiverOf_faithful
#print axioms MethodRecvCert.receiverOf_call_sentinel
#print axioms MethodRecvCert.receiverOf_evil
#print axioms MethodRecvCert.kind_mcall
#print axioms MethodRecvCert.iscall_mcall
#print axioms MethodRecvCert.mcall_inj
#print axioms MethodRecvCert.mcall_neq_call
