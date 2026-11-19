# Emitting certified recursions for non-fold IR traversals — an open problem for external review

*Self-contained problem statement, 2026-07-08. For an external programming-languages / deductive-
verification / verified-compilation reviewer. No prior project knowledge assumed. This is the residual
after the "bounded structural fold" class was solved (§2).*

---

## 0. What we are asking you

We have a self-verifying deductive verifier whose one hard construct — a method that traverses a generic
heterogeneous `Dict[str, Any]` IR — we have *partially* conquered. A **certified catamorphism generator**
now emits proving recursions for the **bounded-fold** shapes (walk-and-accumulate-into-a-fixed-algebra).
The **residual** is a taxonomy of traversals that are **not folds**: they *reconstruct* the tree, *branch
on runtime values*, *compose multiple sub-traversals*, *short-circuit*, or *thread a context map*. Each is
currently research-grade for us — beyond a bounded template — and each remaining `\trusted` stub is one of
these. **Which state-of-the-art techniques (functorial map / tree-rewriting, attribute grammars, monadic /
effectful traversal, refinement-typed narrowing, deductive/relational synthesis, verified compilation of
transformers) let a *verifying compiler* emit certified, terminating, type-safe recursions for these
shapes — under a type-safety+frame-only obligation, byte-identical on existing code, and with no new
trusted axiom?** §6 lists the concrete questions; §7 is the frozen benchmark.

This is **not** a value-modeling or SMT question (those are solved and certified, §2); it is a **code-
generation** question about traversals richer than folds.

---

## 1. The system and its self-verification bootstrap (architecture)

**PyCSL** is a deductive verifier for a statically-analysable subset of Python. It lowers that subset to
**WhyML** (Why3's input language), which generates verification conditions discharged automatically by
**SMT solvers (Alt-Ergo, Z3, CVC5, best-of-N)**. Contracts are Hoare-style (`requires`/`ensures`/`assigns`)
in `#@` comments.

Its trusted base is pinned by a **3-axiom ledger** mechanised in **Rocq 8.20 and Lean 4.29**
(`alt_ergo_correct`, `trusted_contracts_axiom`, `why3_implements_wp_w`). Any extension introducing a new
target-language value shape must **co-land an axiom-free Rocq+Lean certificate** (the *coupling rule*);
the ledger must stay at exactly 3, asserted in CI via `Print Assumptions` / `#print axioms`.

**Self-verification bootstrap.** The WhyML **emitter** (compiler back-end, ~4 kLOC) is written in the
verifiable Python subset; PyCSL verifies a **mirror** of its own emitter. Each emitter method is a
**body-verified** function or a `\trusted` stub (assumed contract). The residual `\trusted` core is
dominated by methods that read/transform the compiler's IR — Python `Dict[str, Any]` trees (string keys;
values int/str/bool/list/nested-dict).

**The decisive scope cut (recurs throughout).** The self-annotation contract is deliberately weak:
`#@ requires True / ensures True / assigns <frame>`. We verify **type-safety** (every projection
well-typed, no `int`/`string` confusion), **frame** (mutates only its declared footprint), and
**termination** (Why3 requires it) — **never** the *value* computed. A reviewer from full functional
verification should recalibrate: we need the weakest interesting guarantee. That cut is what makes the
solved part bounded and, we hope, the residual tractable too.

---

## 2. What is already solved & certified (do NOT re-solve this)

A multi-phase effort (all artifacts committed) decomposed and largely resolved the value/fold problem:

- **L1 — value modeling: SOLVED & CERTIFIED.** A concrete universal-value type
  `pyval = PInt | PStr | PBool | PNone | PList (list pyval) | PDict pydict` with `pydict = DNil | DCons irkey
  pyval pydict` — interned constructor keys (`irkey` enum) + Why3 `compute_in_goal` proof-by-evaluation —
  clears the SMT pathologies (key-lookup, termination) on **both** provers, with an **axiom-free Rocq 8.20 +
  Lean 4.29 certificate** (`Print Assumptions` = "Closed under the global context"). Ledger held at 3.
- **L3 — bounded-fold code generation: SOLVED.** A `GenericFold` recognizer + templater emits, from a
  recognized generic walk, the type-derived `walk`/`walk_dict`/`walk_list` catamorphism over `pyval`/`pydict`
  with a structural `size`-variant. **Each emitted instance is re-proved by Why3** (a template bug ⇒ an
  unprovable instance, never a false proof ⇒ **no new trust**). It handles two result algebras:
  - **A-unit** — walk mutating a by-reference `Set[str]`/`Dict` accumulator (`writes {acc}`, frame checked
    against `#@ assigns`);
  - **A-set** — walk returning a set built by union (a pure `map string bool` + `set_union`, no certificate
    needed).
  Six real emitter methods now self-prove where they were `\trusted`, byte-identical on the 756-program
  reference corpus, no new axiom.

**So: the value type, the fold-to-fixed-algebra shape, termination, and by-ref framing are all done.** The
residual is what is left when the traversal is not a fold-to-a-fixed-algebra.

---

## 3. The residual — five non-fold traversal shapes (the wall)

Every remaining `\trusted` IR-traversal method is (a combination of) these. Each is verified against a live
body; the shared property is that they exceed "walk + accumulate into a fixed algebra".

1. **Tree RECONSTRUCTION (functorial map / rewriting).** Return a *new* IR tree that is the input with some
   nodes rewritten. Example — `_subst_type_in_ir(node, tvar, concrete)`: rebuild the dict preserving keys,
   replacing `Var(name=tvar)` with `Var(name=concrete)`:
   ```python
   new = {}
   for k, v in node.items():
       if k == "name" and v == tvar and node.get("type") == "Var": new[k] = concrete
       else: new[k] = _subst_type_in_ir(v, tvar, concrete)
   return new
   ```
   Needs the emitted recursion to **construct** a `pydict`/`pyval` (build `DCons` cells), not just read it —
   a *catamorphism into the value type itself* (a functorial `map`), with a certificate that the rebuild
   terminates and is well-typed.
2. **VALUE-DEPENDENT branching.** Guards compare a projected value to a **runtime parameter**, not a literal
   (`v == tvar`, `v == concrete`). The solved folds only ever gate on *literal* keys/values (constructor
   discriminants, `pystr_eq s "Assign"`); a comparison against a param is dynamic and currently outside the
   grammar.
3. **COMPOSED multi-algebra traversal.** The method runs *several* sub-traversals of different algebras and
   combines them — e.g. `find_return_type` guards a string-building walk with two boolean predicate walks
   (`_has_return`, `_has_return_with_value`) and does **first-match search** with early-return-in-loop, then
   builds a synthetic result. Three algebras (bool × bool × string) + control flow in one method.
4. **SHORT-CIRCUIT / SEARCH.** `return` inside the walk loop on the first hit; the result is "the first node
   satisfying P", not an accumulation. Not a catamorphism (no uniform fold; the recursion is cut).
5. **CONTEXT-THREADING (inherited attributes).** The walk carries a **context map** (a symbol table) and
   branches on **variable-key lookups** into it — e.g. `_sa_walk(node, where, symtab)` does
   `symtab.get(node["name"])` and raises on a mismatch. The key is computed from the node (not a literal),
   and the context is an extra threaded parameter that itself needs a faithful value model.

A method may combine several (e.g. reconstruction + value-dependent; composed + short-circuit). The
solved fold subsystem recognizes none of them (fail-closed), so they all stay `\trusted`.

---

## 4. Why these are hard here (measured obstacles)

- **Reconstruction needs value *construction* + a termination/soundness certificate.** The solved folds only
  *read* `pyval` (projections closed by the L1 lemma pack). A functorial map must *build* `pyval`; proving it
  terminates and preserves well-formedness is a new certificate obligation (co-landing, axiom-free).
- **Value-dependent guards break the "literal narrowing" discipline.** The solved grammar discharges each
  projection with a constructor/`pystr_eq`-against-a-literal that evaluates by computation. A guard against a
  runtime param (`v == tvar`) is a genuine dynamic string comparison — it re-introduces the SMT string-theory
  cost the interned-key design was built to avoid, unless refinement/flow information supplies it.
- **Composition + short-circuit are not catamorphisms.** A single `let rec … variant {size v}` group models
  one uniform fold. Composed sub-traversals, early return, and value-steered recursion are not a fold; they
  are (respectively) function composition, an effectful `Option`/exception, and a non-structural control flow
  — none expressible by the current type-derived template.
- **Context-threading needs a modeled context + variable-key reads.** A symbol table is another
  `Dict[str, Any]` read by a *computed* key — the very generic-`Any`-map problem, in the inherited-attribute
  position, plus the extra threaded parameter.
- **The scope cut helps but does not trivialize.** type-safety+frame means we need not prove *which* tree is
  produced or *which* node is found — only that the rebuild is well-typed and terminating, the search's
  return type is sound, the context read is in-bounds. That is far weaker than functional correctness, and is
  exactly the leverage we ask the reviewer to exploit.

---

## 5. Constraints bounding admissible solutions

- **Target: WhyML → Why3 → SMT**, automatic proof only (per-goal seconds budget); no interactive proof in
  the emission path.
- **Termination mandatory & SMT-dischargeable** — program `let rec` needs an explicit `variant` whose
  decrease the solver discharges (structural sub-term measures + the L1 lemma pack for reads; a *new* measure
  for constructions).
- **3-axiom ledger fixed** — any new value shape / lemma is **mechanically certified axiom-free** (Rocq 8.20 +
  Lean 4.29), never assumed.
- **Byte-for-byte additivity** — byte-identical emission on the 756-program reference corpus; new capability
  is pattern-gated and inert elsewhere (a poisoned control must flip the gate red once).
- **Per-instance re-proof = no new trust** — the code generator never enters the TCB; a generator bug yields
  an unprovable instance, not a false proof.
- **type-safety + frame + termination only** — never value-faithful; no source↔target functional-equivalence
  obligation is required (though a minimal simulation argument may be desirable — an open question, §6.6).
- **Self-hosting** — the generator is emitter-side code, itself in the verifiable subset (or `\trusted` and
  audited).

---

## 6. Open questions for the reviewer (candidate SOTA in brackets)

1. **Certified functorial map / tree rewriting (shape 1).** How should a verifying compiler emit a
   *reconstructing* traversal (`pyval -> pyval`) with a termination measure and an axiom-free well-formedness
   certificate? *[SYB `everywhere`/`transform`, uniplate; Stratego / term-rewriting strategies; CompCert-style
   verified transformation passes; Coq `Equations`/`Function` for structurally-recursive maps.]*
2. **Value-dependent narrowing without string-theory blowup (shape 2).** Can a guard against a runtime
   parameter be discharged for type-safety via refinement/occurrence typing rather than raw SMT string
   equality? *[occurrence typing — Typed Racket, TypeScript; refinement types — LiquidHaskell, F*; a decidable
   theory of interned strings.]*
3. **Composed + short-circuit traversals (shapes 3, 4).** What is the right way to compile a method that
   composes several algebra-distinct sub-traversals and/or returns early — as effectful/monadic traversal
   (`Option`/exception/state), or as separately-recognized-and-certified helpers glued by first-order
   composition? *[monadic/applicative `Traversable`; algebraic effects & handlers; `Option`/exception effects
   in Why3; defunctionalized composition.]*
4. **Context-threading (shape 5).** How to model an inherited **context map** (symbol table) read by a
   computed key, threaded through the recursion, under type-safety-only? *[attribute grammars (inherited
   attributes); reader/state monads; the same certified `pydict` in argument position + a variable-key read
   lemma.]*
5. **Recognition & synthesis vs. schema.** Where is the boundary between *schematic* (recognize-a-closed-idiom
   + instantiate-a-certified-template, our current cheap+auditable approach) and *synthesis* (search for the
   recursion)? Which residual shapes fall to a few more templates, and which genuinely need synthesis?
   *[syntax-guided synthesis (SyGuS); deductive synthesis; Farzan–Nicolet fold synthesis; recursion-scheme
   detection.]*
6. **Do we need source↔target equivalence?** Under a type-safety+frame contract the emitted recursion need
   not be proved I/O-equivalent to the source traversal. Is that sound to lean on, or does a minimal
   simulation/refinement obligation between the imperative source and the emitted recursion belong in the
   certificate? *[translation validation — Pnueli, Necula; refinement/simulation.]*
7. **Keeping the TCB honest.** Which of the above compose with a conservative axiom-free Rocq+Lean
   certificate, and which secretly trust a decision procedure or a new axiom?

---

## 7. Success criteria — the frozen benchmark

Evaluated against these exact, reproducible committed artifacts (`getting-better/tier3/`, `phase3.md`,
`bigger-build.md`, `test-suite/corpus/conformance/spikes/`):

1. **`_subst_type_in_ir`** (shape 1+2 — reconstruction + value-dependent) emitted as a WhyML recursion that
   **whole-body-proves** (`--fun`, all VCs Valid) under `requires True / ensures True / assigns \nothing`.
2. **`_sa_walk`** (shape 5 — context-threading) proves under its frame.
3. **`find_return_type`** (shapes 3+4 — composed + short-circuit) proves.
4. **Ledger == 3** (`Print Assumptions` / `#print axioms`) — any new value shape mechanically certified.
5. **Byte-diff 0** on the 756-program corpus (pattern-gated, inert elsewhere) + a poisoned control.
6. Discharge within the automatic per-goal SMT budget.

Clearing (1)–(6) for a shape breaks that residual class in practice. A rigorous argument that **no**
verifying-compiler technique can, under these constraints, is an equally valuable closure — it justifies
leaving those methods `TRUSTED(essential)` with a documented, well-posed reason.

---

## 8. One-paragraph brief

*A self-verifying Why3/SMT deductive verifier proves type-safety+frame of most of its own WhyML emitter. It
has certified a universal `pydict` value model (axiom-free Rocq 8.20 + Lean 4.29, 3-axiom ledger) and a
`GenericFold` code generator that emits certified catamorphic recursions for the **bounded-fold** IR
traversals (walk-and-accumulate; six real methods self-proved, no new axiom, byte-diff 0). The **residual**
is five non-fold traversal shapes — tree reconstruction (functorial map), value-dependent branching against
runtime params, composed multi-algebra traversal, short-circuit search, and context-map threading — each
currently research-grade for us. Constraints: automatic SMT only, SMT-dischargeable termination, a fixed
3-axiom certified ledger, byte-identical output on 756 programs, per-instance re-proof (no new trust), and a
type-safety+frame-only obligation (no functional equivalence required). Which combination of functorial-map /
tree-rewriting compilation, refinement/occurrence typing, monadic/effectful traversal, attribute grammars,
and (only if needed) recursion synthesis emits certified terminating recursions for these shapes?*

### Reference artifacts
- Solved value model + fold generator: `bigger-build.md`, `phase3.md`, `getting-better/tier3/wall-plan-v2-phase*.md`
- Certified L1: `src/formal-semantics/rocq/Phase2c_PyValDict.v`, `src/formal-semantics/lean/PyCSL/PyValDict.lean`,
  `test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw`
- The predecessor problem statements (value-modeling → code-generation, now solved):
  `generic-dict-str-and.md`, `generic-dict-str-any-2.md`, `wall-plan-v2-phase2c-stand-alone.md`
- Soundness ledger + LINK-1/2/3: `src/formal-semantics/` (Rocq 8.20 + Lean 4.29)
- Prior-art anchors: SYB / uniplate / Stratego (generic traversal & rewriting); CompCert / CakeML (verified
  compilation); Coq Equations / `Function` (structural recursion & maps); Typed Racket / TypeScript / F* /
  LiquidHaskell (occurrence & refinement typing); algebraic effects & monadic `Traversable`; attribute
  grammars; SyGuS / deductive & fold synthesis; translation validation (Pnueli, Necula).
