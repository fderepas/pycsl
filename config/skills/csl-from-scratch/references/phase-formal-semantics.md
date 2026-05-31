# Phase 6 — Formal semantics in a proof assistant (dual-prover)

Load when starting the Rocq+Lean formalization, when debugging a
soundness or correspondence proof, or when hitting one of the
proof-technique gotchas (forward-vs-backward reasoning, manual
DecidableEq for nested-list inductives, …).

This is the highest-value phase: formal proof reliably finds
WP-vs-eval inconsistency bugs that no testing catches. Expect
2–5 bugs to surface here.

---

> **Squeeze → S2 (formal semantics) + S5 (dual provers).** The
> strongest squeeze: the proof assistant rejects any WP calculus
> that disagrees with the operational semantics. Two independent
> kernels (Rocq + Lean) squeeze further — a curator error in one
> is caught by disagreement in the other.

The *CSL is now expressive enough to be formalized. Mirror the
IR and the WP calculus in a proof assistant.

**Pick a first proof assistant** — Rocq is the obvious choice.
Reasons: mature SerAPI / coq-serapi for downstream automation,
strong inductive-type ecosystem, good for the small-step
operational semantics needed.

**Mirror the IR as inductive types**:

```rocq
Inductive expr : Type :=
  | EInt    (n : Z)
  | EVar    (x : ident)
  | EBinOp  (op : binop) (e1 e2 : expr)
  | ESubscript (arr : ident) (i : expr)
  | ELen    (arr : ident)
  …

Inductive stmt : Type :=
  | SSkip
  | SAssign    (x : ident) (e : expr)
  | SSeq       (s1 s2 : stmt)
  | SIf        (cond : expr) (s_then s_else : stmt)
  | SWhile     (inv : contract_expr) (var : contract_expr)
               (cond : expr) (body : stmt)
  …
```

**Define operational semantics** (small-step or big-step; PyCSL
uses big-step `exec`). Define the WP calculus
(`Inductive wp : stmt -> wp_conts -> exec_state -> Prop`).

**State the soundness theorem**:

```rocq
Theorem pycsl_soundness :
  forall es s out Qn Qr Qc Qb Qe pre_es,
  exec es s out ->
  wp s Qn Qr Qc Qb Qe pre_es es ->
  outcome_post Qn Qr Qc Qb Qe out.
```

**Now do it again in Lean 4**. Two independent kernels increase
soundness confidence: their disagreement on a theorem statement
is a curator error, detectable by the cross-prover diff.

Cite
[`working-with-two-sources-of-truth.md`](../../../../working-with-two-sources-of-truth.md)
for the dual-prover mechanism + cross-prover IR +
canonicalization pipeline.

**Concrete deliverable shape** (use sub-phases; gocsl uses
Phase1-Phase8 with sub-phases 3b, 7a-7d, 8a-8b for managing
fine-grained dependencies):

- `src/formal-semantics/rocq/Phase1_AST.v` — IR as Rocq
  inductives.
- `src/formal-semantics/rocq/Phase2_State.v` — execution state
  + `eval_expr` + `eval_int` + `eval_bool`.
- `src/formal-semantics/rocq/Phase3_SOS.v` — big-step operational
  semantics (`exec`).
- `src/formal-semantics/rocq/Phase3b_Desugar.v` — desugaring
  pass + bisimulation lemma.
- `src/formal-semantics/rocq/Phase4_WP.v` — WP calculus.
- `src/formal-semantics/rocq/Phase5_WhileInv.v` — while
  invariant preservation (standalone).
- `src/formal-semantics/rocq/Phase6_Soundness.v` — **the main
  soundness theorem** (proof by induction on `exec`).
- `src/formal-semantics/rocq/Phase7a_WhyML.v` — WhyML IR types.
- `src/formal-semantics/rocq/Phase7b_WPW.v` — WP semantics for
  WhyML.
- `src/formal-semantics/rocq/Phase7c_StmtGen.v` — stmt → WhyML
  translation (mirrors Module 6).
- `src/formal-semantics/rocq/Phase7d_CorrMain.v` — WP
  correspondence (`wp_gen_correct`).
- `src/formal-semantics/rocq/Phase8a_VcgSound.v` — VCG bridge
  soundness.
- `src/formal-semantics/rocq/Phase8b_SoundnessVerified.v` —
  end-to-end theorem.
- `src/formal-semantics/lean/<Lang>/{AST,State,SOS,WP,Soundness,…}.lean`
  — Lean mirror.
- `src/formal-semantics/audit-plan.md` — third traceability
  matrix: source-language feature → IR node → Rocq theorem →
  Lean theorem → reference test.

The traceability discipline now spans four documents: host
grammar, *CSL annotations, formal IR constructors, formal
soundness arms. Every feature has a row in all four.

## Proof order and strategy (lessons from gocsl)

**Prove soundness FIRST.** `<lang>csl_soundness` is the crown
jewel and catches bugs in eval/wp/SOS that no testing can find.
It's also the proof most resistant to the "deep sub-case" blow-up
because the IH from `induction Hexec` is cleanly scoped.

**Recommended proof order**:

1. **Soundness** (`<lang>csl_soundness`) — induction on `exec`.
   Each `exec` constructor gives an IH that directly applies to
   the corresponding `wp` case. gocsl proved this with ~80 lines.
2. **Desugaring lemmas** (e.g., `switch_desugar_fwd/bwd`) —
   induction on the auxiliary data structure (case list), not on
   `exec`.
3. **WP correspondence** (`wp_gen_correct`) — structural induction
   on stmt. Some cases (SSeq, STryCatch) require
   `functional_extensionality` + `propositional_extensionality`
   to rewrite continuations inside lambda bodies.
4. **Determinism** (`exec_deterministic`) — mechanical but very
   verbose. ~80% handled by automation; the remaining deeply
   nested While/Seq sub-cases are acceptable as Admitted.

**Proof technique: forward reasoning for soundness.**

When `outcome_satisfies` is a `Definition` (not an `Inductive`),
backward reasoning (`apply IH. exact Hwp.`) causes Coq to
unify structurally before reducing, constraining the wrong
continuation. Use forward reasoning instead:

```rocq
(* BAD — Coq unifies Qn with the goal's Qn, not Hwp's *)
apply IHHexec. exact Hwp.

(* GOOD — Coq infers all arguments from Hwp's type *)
exact (IHHexec pre_es _ _ _ _ _ Hwp).

(* GOOD — for composed cases like SSeq *)
exact (IHHexec2 pre_es _ _ _ _ _
         (IHHexec1 pre_es _ _ _ _ _ Hwp)).
```

**Continuation rewriting for SSeq and STryCatch:**

`wp (SSeq s1 s2)` uses `wp s2` inside s1's normal continuation.
`go_wp_w (go_gen (SSeq s1 s2))` uses `go_wp_w (go_gen s2)`.
These are propositionally equal (by IH) but not definitionally
equal. Rewrite with extensionality:

```rocq
assert (Hext : (fun es1 => wp s2 Qn Qr Qc Qb Qp pre_es es1) =
               (fun es1 => go_wp_w (go_gen s2) (go_enc Qn Qr Qc Qb Qp) pre_es es1)).
{ apply functional_extensionality. intro x.
  apply propositional_extensionality. apply IHs2. }
rewrite Hext in H. apply IHs1. exact H.
```

## Bugs discovered during proof (expected — this is the value)

Formal proof work reliably discovers semantic consistency bugs
that are invisible to testing. **Expect to find 2-5 bugs during
the soundness proof attempt.** Examples from gocsl:

| Bug | How discovered | Impact |
|---|---|---|
| `eval_expr` ECmp returned `VInt n | _ => 0` but `eval_int` returned `VInt n | VBool true => 1 | _ => 0` | Switch desugaring proof couldn't bridge `eval_bool (ECmp CmpEq ...)` and `Z.eqb (eval_int ...)` | Fixed by adding `VBool true => 1` to ECmp case |
| SWhile body's break continuation was the *outer* Qb instead of Qn | Soundness proof: break should exit the immediately enclosing loop (→ ONormal), not propagate to enclosing context | Fixed body Qb := Qn |
| SWhile body's continue continuation was just `inv` instead of `inv ∧ var_dec ∧ var_nn` | Soundness proof: continue must also satisfy variant decrease for convergence | Fixed body Qc := body_done |

**These bugs prove that formal semantics is not academic
overhead — it finds bugs in the WP calculus that testing
can't reach**, because they involve *relationships between
functions* (eval_expr ↔ eval_int, wp ↔ go_wp_w) that only
surface when you try to prove the relationship holds.

## Known abstraction gaps (expected — document, don't hide)

Some `wp_gen_correct` cases are NOT provable without model
changes. Document these explicitly as design limitations:

| Gap | Why unprovable | Status |
|---|---|---|
| SDefer | wp pushes to defer stack (`push_defer`); WhyML encoding uses GWSkip. `Qn (push_defer es call) ↔ Qn es` is false in general. | Admitted — needs ghost-state extension in WhyML |
| SPanic | wp passes `eval_expr msg` as panic value; WhyML encoding uses `VNil`. `Qp es (eval_expr msg) ↔ Qp es VNil` is false. | Admitted — needs panic-value threading |
| SFieldAssign (non-EVar) | wp gives `False` for non-variable targets; WhyML skips silently | Admitted — emit error in Module 6 instead |

**Each abstraction gap is a tracked TODO, not a permanent
acceptance.** Close them via Module 6 or WhyML model extensions.

## Lean mirroring discipline

- Keep Lean definitions in sync with Rocq fixes — **the same
  logical bugs exist in both** (gocsl's SWhile Qb bug was
  present in both Rocq and Lean).
- Lean compiles ~5× faster (`lake build` ~5s vs `make proof`
  ~30s), useful for quick structural iteration.
- Lean uses `axiom` for theorems that are `Admitted` in Rocq.
  When a Rocq theorem moves to `Qed`, update Lean to `theorem`
  if possible, otherwise annotate the axiom with a comment
  noting the Rocq proof status.

## Manual `DecidableEq` for nested-list inductives (Lean)

A recurring trap. Lean's `deriving DecidableEq` handler cannot
synthesize an instance for an inductive that mentions itself
through a parametrized container — `inductive Expr | call
(func : Ident) (args : List Expr) | …` fails with "None of the
deriving handlers for class `DecidableEq` applied to `Expr`".
The Rocq side has the same shape via `list_eq_dec expr_eq_dec`,
so the gap is purely on the Lean side.

The robust workaround is **manual mutual recursion + explicit
cross-pair enumeration**:

```lean
mutual
  protected def Expr.decEq : (e1 e2 : Expr) → Decidable (e1 = e2) := …
  protected def Expr.decEqList : (xs ys : List Expr) → Decidable (xs = ys) := …
end

instance instDecidableEqExpr : DecidableEq Expr := Expr.decEq
```

**Gotcha — pattern-ordering does not exclude same-head pairs
from the catch-all**. The tempting compact form

```lean
| .call f args, .call f' args' => /- real check -/
| .call _ _,    _              => Decidable.isFalse (fun h => by cases h)
```

fails because Lean's elaborator checks the catch-all's proof
obligation for **all** `(e1, e2)` matching the second pattern,
including `(.call f args, .call f args)`. `cases heq` on the
reflexive equality leaves `case refl ⊢ False`, which cannot be
discharged. Pattern dispatch at runtime is order-sensitive;
totality checking is not.

The robust fix is to enumerate every cross-constructor pair
explicitly. For an N-constructor inductive this is N(N−1)
arms, each of the form

```lean
| .ctor1 _, .ctor2 _ => Decidable.isFalse (fun heq => by cases heq)
```

Manageable up to ~12 constructors (PyCSL's `Expr` has 9 →
72 cross-pairs). Beyond that, prefer a Bool-valued helper
function (`Expr.beq : Expr → Expr → Bool`) and prove a
separate `decide_eq_of_beq` Lemma to lift it.

Cite `src/formal-semantics/lean/PyCSL/AST.lean` for the
worked example.

## Lean instance citation in the audit-anchor stub

When `#@ proof lean PyCSL.AST.instDecidableEqExpr` cites an
instance, the audit's namespace-aware parser needs to find a
**named** instance declaration (anonymous `instance : Foo` won't
match). Either name the real instance (`instance
instDecidableEqExpr : DecidableEq Expr := …`) or, in the
audit-anchor stub, declare a minimal `instance instFoo : Foo
:= ...` whose body is a placeholder — the stub doesn't compile
under the main `lakefile.lean`; only the audit reads it.

The proof2why3 parser also has a parser surface for instance
signatures. `DecidableEq PyCSL.AST.Expr` won't canonicalize
unless the dotted type path is stripped (mirror of the
`Nat.gcd → gcd` pattern in `_LIBRARY_PREFIX_STRIPS`) and the
type-class head is in `_KNOWN_FN_HEADS`. Citing a new
type-class instance in a `#@ proof lean` directive may
require both extensions — concrete edits at
`src/pycsl/proof2why3/parser.py`.
