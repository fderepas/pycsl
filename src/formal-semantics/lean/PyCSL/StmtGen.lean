/-
  StmtGen.lean — Statement Generator
  Defines gen : Stmt → WhyMLStmt, the formal model of Module 6's
  translation. Module 6 = `src/pycsl/Module6_WhyMLTranspiler.py`
  (facade) + `src/pycsl/module6_whyml/` (10 emission mixins,
  post-refactor). The concrete Python implementation of `gen` lives
  in `src/pycsl/module6_whyml/statements.py` (statement dispatchers)
  and `src/pycsl/module6_whyml/expressions.py` (expression dispatchers).

  SFor is inlined to keep gen structurally recursive (avoids the
  termination issue with gen (desugar ...)). A lemma in CorrLoops confirms
  the inlined version is propositionally equal to gen (desugar (SFor ...)).
-/
import PyCSL.AST
import PyCSL.DesugarDef   -- for forIdx
import PyCSL.WhyML

-- genLiftContinue: mirrors liftContinue for WhyMLStmt.
-- Replaces shallow WRaise excContinue with WSeq inc (WRaise excContinue).
def genLiftContinue (inc : WhyMLStmt) : WhyMLStmt → WhyMLStmt
  | .wRaise .excContinue    => .wSeq inc (.wRaise .excContinue)
  | .wSeq w1 w2             => .wSeq (genLiftContinue inc w1) (genLiftContinue inc w2)
  | .wIf c w1 w2            => .wIf c (genLiftContinue inc w1) (genLiftContinue inc w2)
  | .wTryCatch body exc h   => .wTryCatch (genLiftContinue inc body) exc
                                           (genLiftContinue inc h)
  | other                   => other

-- gen: formal model of Module 6's WhyML generator.
-- Python correspondent: dispatch in
-- `src/pycsl/module6_whyml/statements.py:_stmts_to_whyml` (~line 1034)
-- which routes to per-stmt `_handle_*_stmt` handlers in the same file.
def gen : Stmt → WhyMLStmt
  | .skip                      => .wSkip
  | .assign x e                => .wAssign x e
  | .augAssign x op e          => .wAugAssign x op e
  | .arraySet arr i v          => .wArraySet arr i v
  | .seq s1 s2                 => .wSeq (gen s1) (gen s2)
  | .ite cond t f              => .wIf cond (gen t) (gen f)
  | .while_ inv var cond body  => .wWhile [inv] [var] cond (gen body)

  -- SFor inlined: see design note in StmtGen.lean header
  | .for_ x arr inv var body _ =>
      let inc := WhyMLStmt.wAugAssign forIdx .add (.int 1)
      .wSeq (.wAssign forIdx (.int 0))
            (.wWhile [inv] [var]
                     (.binop .sub (.len arr) (.var forIdx))
                     (.wSeq (.wAssign x (.subscript arr (.var forIdx)))
                            (.wSeq (genLiftContinue inc (gen body)) inc)))

  -- SReturn: set \result then raise Return exception
  | .ret e                     => .wSeq (.wAssign "\\result" e) (.wRaise .excReturn)

  | .continue_                 => .wRaise .excContinue
  | .break_                    => .wRaise .excBreak
  | .assert_ cond msg          => .wAssert cond msg
  | .tupleUnpack _ _           => .wSkip
  | .ghostDecl x t e           => .wGhostDecl x t e
  | .ghostAssign x t op e      => .wGhostAssign x t op e
  | .label_ L                  => .wLabel L
  | .raise_ exc                => .wRaise (.excNamed exc)
  | .tryCatch body exc handler => .wTryCatch (gen body) exc (gen handler)

  -- Phase 6 field ops: flat-key field-state model — `self.f` is the
  -- synthetic variable `selfId ++ "." ++ f`, so field (aug-)assign
  -- generates the WhyML (aug-)assign to that key (mirrors the wp/SOS arms).
  | .fieldAssign selfId f e        => .wAssign (selfId ++ "." ++ f) e
  | .fieldAugAssign selfId f op e  => .wAugAssign (selfId ++ "." ++ f) op e

  -- Phase 8 concurrency: transparent in Hoare model
  | .critical _ body           => gen body
  | .threadEntry body          => gen body
  -- Phase 7 acquires/releases: Hoare-model no-op (emit wSkip)
  | .acquires _                => .wSkip
  | .releases _                => .wSkip
  -- Phase 8 lambda: .call is an opaque statement (closures not in WhyML).
  -- Emit wSkip — parity with .fieldAssign and .tupleUnpack.
  | .call _ _ _                => .wSkip
  -- Phase 8 lambda construction: binds a closure value (non-emittable, like .call)
  | .lambda _ _ _              => .wSkip

-- Phase 8: isEmittable — True for all Stmt constructors EXCEPT .call.
-- WhyML has no closure model, so gen (.call ...) = .wSkip does NOT
-- correspond to wp (.call ...) (which is a behavioural formula).
-- wpGenCorrect is therefore stated only for emittable stmts.
def isEmittable : Stmt → Prop
  | .seq s1 s2        => isEmittable s1 ∧ isEmittable s2
  | .ite _ s1 s2      => isEmittable s1 ∧ isEmittable s2
  | .while_ _ _ _ b   => isEmittable b
  | .for_ _ _ _ _ b _ => isEmittable b
  | .tryCatch b _ h   => isEmittable b ∧ isEmittable h
  | .critical _ b     => isEmittable b
  | .threadEntry b    => isEmittable b
  | .call _ _ _       => False
  | .lambda _ _ _     => False
  | _                 => True
