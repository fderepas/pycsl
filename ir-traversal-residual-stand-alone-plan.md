# ir-traversal-residual-stand-alone-plan.md — Breaking the non-fold traversal wall: plan

*Self-contained plan, 2026-07-08. Companion and answer to the open-problem statement
"Emitting certified recursions for non-fold IR traversals". Assumes its §1–§2 context: the certified
`pyval`/`pydict` value model (L1), the `GenericFold` recognizer+templater with algebras A-unit and
A-set (L3), the 3-axiom ledger (Rocq 8.20 + Lean 4.29), per-instance re-proof, byte-for-byte
additivity, and the type-safety+frame+termination-only scope cut.*

**Thesis.** None of the five residual shapes needs synthesis, and two of them (value-dependent
branching; most of context-threading's difficulty) dissolve under the project's own scope cut once
guards are classified correctly. The wall decomposes into **one classification insight (C), three
result-algebra template extensions (T1 map, T2 option, T3 env-threaded), one decomposition pass
(D), and two small co-landed certificates** — all inside the existing fail-closed, per-instance-
re-proof architecture, ledger fixed at 3. Synthesis (SyGuS / Farzan–Nicolet) is explicitly rejected
for this benchmark: it buys no shape the templates don't cover and costs auditability.

---

## 0. Solution map (shapes → mechanisms → benchmark)

| Residual shape (§3 of problem stmt) | Mechanism | Benchmark method cleared |
|---|---|---|
| 2. Value-dependent branching | **C** — guard classification + opaque booleans + defensive totalization | (unblocks 1 and 5) |
| 1. Tree reconstruction | **T1** — functorial-map algebra (codomain `pyval`/`pydict`) | `_subst_type_in_ir` (with C) |
| 4. Short-circuit / search | **T2** — option algebra (first-match fold) | half of `find_return_type` |
| 3. Composed multi-algebra | **D** — traversal outlining; glue is ordinary WP | `find_return_type` (with T2) |
| 5. Context-threading | **T3** — env-parameter fold + `sdict` + `raises` | `_sa_walk` |

Build order (risk-adjusted): **C → T2 → T1 → D → T3.** C is a recognizer change, near-free, and
unblocks two shapes; T2 is the smallest algebra delta; T3 carries the largest single certificate.

---

## 1. C — Guard classification (dissolves shape 2)

**Observation.** Under `requires True / ensures True`, a guard's truth value matters to a VC only if
the guard *establishes type safety* of a branch. In the residual methods, guards like `v == tvar`
select *which rewrite happens*; they never justify a projection. Therefore the solver never needs to
reason about them.

**Mechanism.** The recognizer classifies every guard:

- **Structural discriminant** — literal comparison that narrows the `pyval` shape
  (`node.get("type") == "Var"`, constructor tests). Stays in the solved interned-key /
  `compute_in_goal` discipline. Unchanged.
- **Semantic guard** — comparison against a runtime parameter or computed value (`v == tvar`,
  `v == concrete`). Compiled to a **concretely defined** `pystr_eq : string → string → bool`
  (definitional, not abstract — nothing uninterpreted enters the theory) whose **result no VC
  constrains**. Both arms are proved type-safe independently. String theory is never invoked,
  because a boolean the goal doesn't constrain costs the solver nothing.

**Companion technique — defensive totalization.** Wherever a projection's safety *could* depend on
flow, the emission makes it total instead: every partial projection compiles to `option` with an
explicit failure arm (default value or exception). Type safety then never depends on a flow fact.
This is the single load-bearing trick reused by T1, T2, and T3.

**What is deliberately NOT built:** occurrence typing / refinement typing (Typed Racket,
LiquidHaskell, F\*). That machinery exists for guards that *do* carry safety information; importing
it here would over-solve shape 2 and add a trusted engine (violating Q7).

**Mechanical safety check (the one residual brick, §7).** The recognizer must flag any projection
whose type safety is dominated *only* by a semantic guard (e.g. "this key exists because we just
compared it"). For such a method, opaque-boolean compilation is insufficient and defensive
totalization changes the method's shape (an explicit failure arm the source lacks) — the method is
either normalized at source or stays `TRUSTED(essential)` with this documented reason. Detection is
syntactic (guard-dominance on the recognizer's parse), so the wall's only possible remaining brick
is found mechanically, not by surprise.

**Cost.** Recognizer-side only; no new WhyML types; no certificate; ledger untouched.

---

## 2. T1 — Functorial-map algebra (shape 1: reconstruction)

**Kill the stated obstacle first.** "Construction needs a new termination measure" is not real: the
`variant` decreases on the **input** — every recursive call in `_subst_type_in_ir` is on a sub-term
of `node`, exactly as in the solved reads-only folds. Building `DCons` cells on the way back up is
constructor application, total by definition. And the frame is *easier* than A-unit: the WhyML
emission is purely functional (returns a fresh `pydict`), so `assigns \nothing` is trivial.
Reconstruction in WhyML is simpler than in Python, not harder.

**Mechanism.** Extend the fold family with result algebra = the value type itself. Same
`walk`/`walk_dict`/`walk_list` skeleton, same `size` variant, per-instance rewrite-rule hole
(defunctionalized, as today — no higher-order WhyML in the emission path). Skeleton:

```whyml
let rec subst_walk (v: pyval) : pyval
  variant { size v }
= match v with
  | PInt _ | PStr _ | PBool _ | PNone -> v
  | PList l  -> PList (subst_list l)
  | PDict d  -> PDict (subst_dict d)
  end
with subst_dict (d: pydict) : pydict
  variant { dsize d }
= match d with
  | DNil -> DNil
  | DCons k v rest ->
      (* HOLE: per-instance rewrite — structural discriminants narrow;
         semantic guards are opaque booleans (C) *)
      if <structural-tests> && pystr_eq <proj> <param>
      then DCons k <replacement> (subst_dict rest)
      else DCons k (subst_walk v) (subst_dict rest)
  end
with subst_list (l: list pyval) : list pyval
  variant { lsize l }
= match l with Nil -> Nil | Cons x r -> Cons (subst_walk x) (subst_list r) end
```

**New certificate obligation (the only one).** If `pyval` carries a well-formedness invariant
(interned `irkey` keys), co-land **map-preserves-wf**: `wf_pyval v → wf_pyval (map v)` — one
structural induction, proved once at *template* level in Rocq+Lean (axiom-free; keys are preserved
from input, so preservation is by the same induction as `size`), re-checked per instance by Why3.

**Prior art anchored.** uniplate `transform` / SYB `everywhere` / Stratego `topdown(try(rule))` for
the shape; CompCert-style per-pass proof replaced by the cheaper **per-instance re-proof** (the
templater never enters the TCB: a template bug ⇒ unprovable instance, never a false proof).

---

## 3. T2 — Option algebra (shape 4: short-circuit / search)

**Reframe.** "Not a catamorphism (the recursion is cut)" is true of the *control flow*, false of the
*function computed*. First-match search **is** the fold into `option pyval` with the
short-circuiting combining step:

```whyml
let rec find_walk (v: pyval) : option pyval
  variant { size v }
= if <p v> (* structural tests; semantic guards opaque per C *)
  then Some v
  else match v with
       | PDict d -> find_dict d
       | PList l -> find_list l
       | _ -> None
       end
with find_dict (d: pydict) : option pyval
  variant { dsize d }
= match d with
  | DNil -> None
  | DCons _ v rest ->
      match find_walk v with Some x -> Some x | None -> find_dict rest end
  end
(* find_list analogous *)
```

Same skeleton, same variant; **A-option joins A-unit and A-set as a sibling algebra**. The
`Some _ → acc` arm is the early return. No effect handlers, no exceptions needed here (reserve Why3
exceptions for source-level `raise`, §5); the option algebra keeps contracts effect-free and
SMT-friendly.

**The real work is recognition, not certification:** mapping imperative
`for … : if p: return x` onto the option fold. Certification-side, T2 is the existing fold
certificate with a new algebra — no new value shape, no ledger movement.

---

## 4. D — Traversal outlining (shape 3: composed multi-algebra)

**Reframe.** Three algebras in one method is hard only because the *method* is the unit of
recognition. Make the *traversal* the unit:

1. The recognizer identifies each **maximal traversal sub-expression** in the method body
   (`_has_return` → existing bool fold; `_has_return_with_value` → existing bool fold; the
   first-match loop → T2; any rebuild → T1).
2. Each is emitted (**outlined**) as its own certified `let rec`, re-proved per instance as usual.
3. The composing method becomes a **non-recursive, first-order function** calling the outlined
   recursions — verified by the ordinary WP pipeline with **no template at all**.

This is standard procedure extraction (the inverse of inlining). It composes cleanly with
per-instance re-proof and adds zero certification concepts. Composition of certified pieces by
first-order glue is exactly what a deductive verifier is already good at.

---

## 5. T3 — Env-threaded fold + `sdict` (shape 5: context-threading)

**Inherited attributes, concretely.** Attribute-grammar inherited attributes = one extra parameter
threaded down the fold (extended at binder nodes if the source extends it). The `variant` remains
`size node`; termination is untouched by the environment.

**The symbol table is NOT `pydict`.** Its keys are runtime strings, not interned constructors, so
introduce a second, deliberately boring datatype:

```whyml
type sdict = SNil | SCons string pyval sdict

let rec slookup (k: string) (s: sdict) : option pyval
  variant { s }
= match s with
  | SNil -> None
  | SCons k' v rest -> if str_eq k k' then Some v else slookup k rest
  end
```

Two facts keep computed-key reads inside the solved discipline: (a) `str_eq`'s result is program
code that **no VC constrains** (insight C again — which entry is found is a value question, out of
scope); (b) the read is safe by construction because it returns `option` and the `None` arm is
explicit (defensive totalization). No string theory enters any VC.

**Source-level `raise` on mismatch** compiles to a Why3 exception with `raises { SAError }` in the
contract — exceptions are already inside `why3_implements_wp_w` (axiom 3), so the ledger does not
move. (Alternative: a `result` type; choose per method by which keeps the mirror closer to source.)

**Certificate co-landing (second and last new certificate).** `sdict` + `slookup` totality/
termination + an in-bounds/option-shape lemma pack: ordinary inductive datatype + defined functions,
one induction each, Rocq 8.20 + Lean 4.29, `Print Assumptions` / `#print axioms` closed. Ledger = 3.

---

## 6. Per-benchmark discharge plan (frozen criteria §7 of problem stmt)

1. **`_subst_type_in_ir`** (shapes 1+2) = **T1 + C**. Structural discriminants (`"type" == "Var"`,
   key `"name"`) stay interned/computed; `v == tvar` and the `concrete` write are semantic —
   opaque `pystr_eq` + replacement value `PStr concrete` (well-typed by construction). Whole-body
   `--fun` proof under `requires True / ensures True / assigns \nothing`; frame trivial (pure
   rebuild). Expected VC profile ≈ solved folds + the wf-preservation instance.
2. **`_sa_walk`** (shape 5) = **T3 + sdict + raises**. Env parameter `symtab: sdict`; node-name
   projection via existing L1 pack; `slookup` result matched totally; mismatch arm raises
   `SAError`; frame per its `#@ assigns`.
3. **`find_return_type`** (shapes 3+4) = **D + T2 + existing bool folds**. Outline
   `_has_return`, `_has_return_with_value` (already-solved A-set/A-unit shapes), outline the
   first-match walk as T2; the remaining method body is straight-line string assembly — ordinary WP.
4. **Ledger == 3**: only two co-landed certificates (map-preserves-wf at template level; `sdict`
   pack), both axiom-free inductions; CI `Print Assumptions` / `#print axioms` unchanged.
5. **Byte-diff 0 + poisoned control**: each of C/T1/T2/T3/D is pattern-gated and fail-closed; the
   corpus has grown (781 files observed vs the frozen 756) — **re-pin the benchmark corpus count**
   before starting so "byte-diff 0" is against a fixed set.
6. **SMT budget**: T1/T2 instances have the same match-on-constructors profile as the solved folds;
   reuse `compute_in_goal` for structural discriminants. The only new solver load is the
   wf-preservation instance (bounded, structural). No string theory anywhere by construction.

---

## 7. Honest residual & rejected alternatives

**The one possible remaining brick.** A method where a *semantic* guard genuinely guards type
safety (projection dominated only by a runtime comparison). C detects this mechanically
(guard-dominance on the recognizer parse). Resolution per method: normalize the source (you own
it — self-hosting means "meet the recognizer halfway" is legitimate and cheap), accept the
defensive-totalization shape change, or document `TRUSTED(essential)` with this precise reason.
That last outcome is the problem statement's own "well-posed closure" and is acceptable.

**Q6 (equivalence) — keep the scope cut; add the free validator.** The certificate honestly says
"the WhyML *model* is type-safe/framed/terminating"; transfer to the Python source rides the same
mirror link the six solved folds already use — no *new* obligation. The cheap strengthening: the
recognizer already **is** a translation validator (fail-closed; its parse records exactly which
projections and recursion structure the emission mirrors). Persist that correspondence as a
per-instance conformance artifact. Do **not** add a simulation proof; it buys little under
type-safety-only and costs the automatic-proof budget.

**Rejected: synthesis (Q5).** SyGuS / deductive / fold synthesis covers no benchmark shape the
templates miss, introduces a search procedure into an auditable pipeline, and its output would need
per-instance re-proof anyway — at which point it is a worse templater. Revisit only if recognition
fails on code that cannot be source-normalized.

**Rejected: refinement/occurrence typing (Q2).** The only bracketed candidate that would smuggle a
new trusted engine into the TCB (violating Q7), to solve a problem that classification C shows does
not exist under the scope cut.

**Rejected: effect handlers / monadic infrastructure (Q3).** The option algebra and Why3's native
exceptions cover shapes 3–4 with zero new machinery; a `Traversable`/handler layer is structure the
SMT backend would pay for without any VC getting easier.

---

## 8. Audit-trail note for the external reviewer

The problem statement's reference artifacts `getting-better/tier3/`, `phase3.md`,
`bigger-build.md`, `src/formal-semantics/rocq/Phase2c_PyValDict.v`, and the predecessor statements
are **not reachable on public `main`** as of 2026-07-08 (the conformance-spikes directory is).
Commit them (and re-pin the corpus count, §6.5) before circulating the problem statement — a
reviewer who clones `main` cannot currently reach the frozen benchmark they are asked to evaluate
against.

---

## 9. One-paragraph brief (mirror of the problem statement's §8)

*The five non-fold residual shapes fall to schema, not synthesis. Classifying guards into
structural discriminants (solved discipline) versus semantic guards compiled as unconstrained
concrete booleans — plus defensive totalization of partial projections — dissolves value-dependent
branching and removes string theory everywhere. Reconstruction is the fold family with the value
type as result algebra (variant on the input; construction is total; frame trivial because the
emission is pure) plus one template-level map-preserves-wf certificate. Short-circuit search is the
fold into `option`. Composed methods are outlined into separately-certified traversals glued by
ordinary first-order WP. Context-threading is an environment parameter (inherited attribute) plus a
second string-keyed `sdict` whose option-valued lookup keeps computed-key reads type-safe without
constraining any equality. Two small axiom-free certificates co-land; the ledger stays at 3;
everything is pattern-gated, fail-closed, per-instance re-proved, byte-diff 0. The only detectable
residual is a projection whose safety depends on a semantic guard — found mechanically by
guard-dominance, resolved by source normalization or a documented `TRUSTED(essential)`.*
