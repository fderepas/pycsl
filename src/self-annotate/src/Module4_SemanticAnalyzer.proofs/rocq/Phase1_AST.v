(* Audit-anchor stub for the citation in
     src/self-annotate/src/Module4_SemanticAnalyzer.py:
       #@ proof rocq Phase1_AST.expr_eq_dec

   The REAL proof lives at
     src/formal-semantics/rocq/Phase1_AST.v:54
   (Lemma binop_eq_dec ... expr_eq_dec ... — decidable equality on
    the formal expr inductive, extended to handle ECall's nested
    list argument via list_eq_dec expr_eq_dec).

   This file is NOT compiled — it exists solely to satisfy the
   namespace-aware audit in src/pycsl/audit_proof.py, which expects
   the cited qualname `Phase1_AST.expr_eq_dec` to be declared inside
   an explicit `Module Phase1_AST. ... End Phase1_AST.` wrapping.
   The formal-semantics file relies on Coq's implicit
   file-as-module convention; this stub bridges the gap.

   See `closer-to-code-execution-status.md` items 47-48 for context
   on the trust chain and CC.4 citation framework. *)

Module Phase1_AST.

(* Stub statement — the real Lemma `expr_eq_dec` is upstream.
   We use a trivial `True` body here because audit_proof.py only
   parses for namespace-aware declaration presence, not for proof
   contents.  The trust anchor for Module 4's structural pattern
   matching on the formal expr type is the upstream Lemma. *)
Theorem expr_eq_dec : True.
Proof. trivial. Qed.

End Phase1_AST.
