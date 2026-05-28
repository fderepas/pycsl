(* Phase6d_StmtGen.v — Statement Generator
   Defines gen : stmt → whyml_stmt, the formal model of Module 6's
   translation. Module 6 = the `src/pycsl/module6_whyml/` subpackage
   plus the `src/pycsl/Module6_WhyMLTranspiler.py` facade (post-refactor
   layout since commits 196aaf2/5e10f38/e381ddf/7546238). The concrete
   Python implementation of `gen` lives in
   `src/pycsl/module6_whyml/statements.py` (statement dispatchers) and
   `src/pycsl/module6_whyml/expressions.py` (expression dispatchers).

   Design notes:
   - Every stmt constructor maps to the whyml_stmt it generates.
   - SFor is inlined (rather than calling gen (desugar ...)) to keep gen
     a structurally recursive Fixpoint.  A separate lemma (wp_gen_for_eq)
     in Phase6f_Corr_Loops confirms the inlined version equals
     gen (desugar (SFor ...)).
   - gen_lift_continue mirrors lift_continue from Phase3b_DesugarDef. *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase3b_DesugarDef.   (* for for_idx *)
Require Import Phase6_WhyML.
Open Scope string_scope.
Open Scope Z_scope.

(* ===== gen_lift_continue: mirrors lift_continue for whyml_stmt ===== *)
(* Replaces shallow WRaise ExcContinue with WSeq inc (WRaise ExcContinue).
   "Shallow" = recurse into WSeq/WIf/WTryCatch but NOT into WWhile. *)

Fixpoint gen_lift_continue (inc w : whyml_stmt) : whyml_stmt :=
  match w with
  | WRaise ExcContinue       => WSeq inc (WRaise ExcContinue)
  | WSeq w1 w2               => WSeq (gen_lift_continue inc w1) (gen_lift_continue inc w2)
  | WIf c w1 w2              => WIf c (gen_lift_continue inc w1) (gen_lift_continue inc w2)
  | WTryCatch body exc h     => WTryCatch (gen_lift_continue inc body) exc
                                          (gen_lift_continue inc h)
  (* WWhile and leaves: pass through unchanged *)
  | other                    => other
  end.

(* ===== gen: formal model of Module 6's WhyML generator =====
   Python correspondent: dispatch in
   `src/pycsl/module6_whyml/statements.py:_stmts_to_whyml` (line ~1034)
   which routes to per-stmt `_handle_*_stmt` handlers in the same file. *)

Fixpoint gen (s : stmt) : whyml_stmt :=
  match s with
  | SSkip                     => WSkip
  | SAssign x e               => WAssign x e
  | SAugAssign x op e         => WAugAssign x op e
  | SArraySet arr i v         => WArraySet arr i v
  | SSeq s1 s2                => WSeq (gen s1) (gen s2)
  | SIf cond t f              => WIf cond (gen t) (gen f)
  | SWhile inv var cond body  => WWhile inv var cond (gen body)

  (* SFor is inlined: SFor x arr inv var body →
       WSeq (WAssign for_idx 0)
            (WWhile inv var (len arr - for_idx)
                    (WSeq (WAssign x arr[for_idx])
                          (WSeq (gen_lift_continue inc (gen body)) inc)))
     where inc = WAugAssign for_idx OpAdd 1.
     This exactly mirrors desugar's output passed through gen. *)
  | SFor x arr inv var body =>
      let inc := WAugAssign for_idx OpAdd (EInt 1) in
      WSeq (WAssign for_idx (EInt 0))
           (WWhile inv var
                   (EBinOp OpSub (ELen arr) (EVar for_idx))
                   (WSeq (WAssign x (ESubscript arr (EVar for_idx)))
                         (WSeq (gen_lift_continue inc (gen body)) inc)))

  (* SReturn: set \result then raise Return exception *)
  | SReturn e                 => WSeq (WAssign "\result" e) (WRaise ExcReturn)

  | SContinue                 => WRaise ExcContinue
  | SBreak                    => WRaise ExcBreak
  | SAssert cond msg          => WAssert cond msg
  | STupleUnpack _ _          => WSkip     (* simplified *)
  | SGhostDecl x t e          => WGhostDecl x t e
  | SGhostAssign x t op e     => WGhostAssign x t op e
  | SLabel L                  => WLabel L
  | SRaise exc                => WRaise (ExcNamed exc)
  | STryCatch body exc handler => WTryCatch (gen body) exc (gen handler)

  (* Phase 6 field ops: Hoare-model placeholder *)
  | SFieldAssign _ _ _        => WSkip
  | SFieldAugAssign _ _ _ _   => WSkip

  (* Phase 8 concurrency: transparent in Hoare model *)
  | SCritical _ body          => gen body
  | SThreadEntry body         => gen body
  end.
