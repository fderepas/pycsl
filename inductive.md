# Plan: `#@ inductive` predicates — implementation plan derived from `inductive-spec.md`

Companion to `inductive-spec.md`. The spec is the normative **"what must hold"** (surface §3,
soundness §7, lowering §9, validation §11). This plan is the **"how we build it, in what order,
behind which gates."** Read both together; the spec owns the *meaning*, this owns the *construction*.

`#@ inductive` is the second of the companion trio (with `#@ lemma`, see `lemma.md`, and typed
quantifiers): inductive predicates **define** least-fixpoint relations over `#@ datatype` structures;
lemma functions **prove** their universally-quantified consequences by induction. The two are a
designed pair — P3 here has a hard dependency on the lemma feature.

Headline: like `#@ lemma`, this is **mostly reuse**. PyCSL already has the module-level multi-line
**block-folding** (`#@ act`/`#@ happy`), the `#@ datatype` parse→IR→preamble pipeline (the closest
sibling), and preamble logic-declaration emission. The genuinely-new work is (1) the
`#@ inductive`/`#@ rule` surface, (2) one Module-6 preamble emitter (`inductive p (…) = | Rule : … end`),
and (3) the **Module-4 strict-positivity soundness pass** — the heart, because a non-positive clause
admits an inconsistent least fixpoint (proves `False`). Everything else is plumbing or reuse.

---

## §0 — Reuse map (why this is code-ready)

| Spec demand | Already in the tree (file:line) | New work? |
|---|---|---|
| Multi-line module block: header `#@ inductive even(n:int):` + 4-space-indented `#@ rule …` lines | `Module1_Ingestor.py`: `_BLOCK_HDRS`/`_match_block_hdr` (:67-78) + `_fold_blocks` (:215-246) — identical folding for `act NAME:` / `happy NAME:` | **Minor** — add an `_INDUCTIVE_HDR` regex (captures the *signature*, not just a bare name) to `_BLOCK_HDRS`; folder unchanged |
| Module-level `datatype` sibling: parse → IR → preamble `type` | `Module2_Parser.py` `DatatypeDecl` (:621) + grammar (:942) + transformer (:1078); `Module3_Weaver` registration (:272-278); `Module5_IREmitter` `type_decls` (:77-87); `preamble.py::_emit_type_decls`/`_fmt_variant` (:609-660) | **No** — mirror it for `InductiveDecl` |
| Rules reference datatype constructors + `match`-style terms | constructor registry (`Module5` :77-87), constructor lowering (`expressions.py`), `\is_ctor`/`\payload` | **No** — reuse in rule-term lowering |
| Preamble logic decls emitted in dependency order (types → axioms → functions) | `Module6_WhyMLTranspiler.py` assembly (:357-394): `_emit_type_decls` (:360) → `_emit_preamble_axioms` (:367) → functions (:392-394) | **Minor** — insert an `_emit_inductive_decls` *between* types and axioms (rules use constructors; axioms/contracts use the predicate) |
| Pure functions usable as logic symbols in premises | `module5/memoization_rt.py::_detect_purity`; `let function` emission `functions.py:317` | **No** — premises may call pure fns (§7.5) |
| `#@ proof rocq\|lean` → `axiom` (the *contrast*: trusted vs an inductive's checked least-fixpoint) | `preamble.py:482-537` | **No** |
| Module-level Module-4 validation home (datatypes/shared/happy) | `Module4_SemanticAnalyzer.py` `visit_Module` (~:500-521) + `_validate_happy`/`_validate_mutex_invariant_scope` | **Yes** — a new `_validate_inductive` lives here (§3) |
| The induction principle that discharges `\forall x. wf(x)⇒P(x)` | **NOT YET BUILT** — supplied by `#@ lemma` (recursive lemma = IH); see `lemma.md` | **Dependency** — P3 needs the lemma feature |

**Net new code:** the `#@ inductive`/`#@ rule` surface (M1 header regex, M2 decl+grammar+transformer,
M3 register, M5 IR), the `_emit_inductive_decls` preamble emitter (M6), and the Module-4
strict-positivity pass (§3). Plus the 5-surface doc-coherency.

---

## §1 — R0 pre-flight: write the Gate-A drivers FIRST (demand-driven)

Step 0; no source change until the drivers exist and fail *for the right reason* (today: `#@ inductive`
does not parse). Drivers go in `test-suite/corpus/pycsl-reference/` at the next free numbers
(**0555+** at time of writing — 0554 is now the stateful-mixin driver). Spec §10/§11 dictate the set:

**Positive (flip to PASS as each phase lands):**
1. **P1 flagship** — `inductive even(n: int)` with `even_zero`/`even_step`; a contract uses `even(k)`;
   introduction proves `even(4)`.
2. **P2** — mutually-inductive `wf(x: Json), wf_spine(s: Json)` carving valid JSON out of the collapsed
   type (spec §3); proves `wf(JArr(JInt(1), JNil))`.
3. **P2 inversion** — `not wf(JArr(JInt(2), JInt(3)))` proved by inversion (the tail satisfies no
   `wf_spine` rule) — the carving-correctness witness.
4. **P3 relational** — `reaches(g, a, b)` over a small (cyclic) graph: prove a reachability fact;
   a universally-quantified consequence discharged via a `#@ lemma` (depends on the lemma feature).

**Negative / anti-soundness (commit `# pycsl-expected: FAIL`, STAY failing — the positivity proof):**
5. **Non-strictly-positive** rule (the defined predicate under negation / in an implication antecedent)
   → **rejected** (spec §7.1). The lynchpin.
6. **Bad conclusion shape** — a rule whose consequent is not an application of a defined predicate →
   rejected (§7.2).
7. **Arity mismatch / partial application** of a predicate → rejected (§7.3).
8. **Executable-position use** — calling an inductive predicate from runtime Python → rejected (§7.4).

**Exit:** 8+ committed drivers; positives FAIL at parse today, negatives FAIL and *stay* failing.

---

## §2 — Code-ready staged plan (supersedes spec §10 for execution)

Each stage: **entry** = prior exit + its driver committed; **exit** = driver flips/holds + full
reference sweep clean + **byte-identical non-mixin/non-inductive corpus** (emission-identical gate,
`PYTHONHASHSEED=0`, all four memory models — the directives are additive) + `bin/doc-coherency.py
--check` green.

### S0 — surface + parse (mirror `#@ datatype` + the block-folder)
- *First files:* `Module1_Ingestor.py` — add `_INDUCTIVE_HDR` to `_BLOCK_HDRS` (:69) and `'inductive '`
  to `_MODULE_PREFIXES` (:23); the header regex must capture the **signature(s)** (`even(n: int)`,
  and `a(..), b(..)` for mutual), unlike the bare-name `happy`/`act` headers. `Module2_Parser.py` —
  `class InductiveDecl` (after `DatatypeDecl` :621), grammar `inductive_decl` + `inductive_rule`
  (near :942), transformer (near :1078). `Module3_Weaver.py` — register `node.csl_inductives`
  (mirror datatype :272-278).
- *Exit:* the P1 flagship parses to `--no-proof` without error.

### S1 — IR + Module-6 preamble emission (`inductive … = | Rule : … end`)
- *First files:* `Module5_IREmitter.py` — `inductive_decls` IR (mirror datatype loop :77-87): name(s),
  signature, `[(rule_name, horn_ir)]`. `module6_whyml/preamble.py` — new `_emit_inductive_decls`
  rendering each rule `| RuleName : forall binders. prem1 -> … -> concl` (lower premises/conclusion via
  `_expr_to_whyml` with `_in_spec`, reusing constructor lowering). `Module6_WhyMLTranspiler.py` —
  call it **between** `_emit_type_decls` (:360) and `_emit_preamble_axioms` (:367).
- **Gate-B feasibility spike (first):** hand-write the target `.mlw` for the P1 flagship
  (`inductive even (n:int) = | Even_zero : even 0 | Even_step : forall m:int. even m -> even (m+2) end`)
  and run it through the installed Why3 to confirm the syntax + that a contract `requires { even k }`
  type-checks and introduction discharges. (Why3 has native `inductive`; pin the surface.)
- *Exit:* P1 flagship PASSES (introduction proves `even(4)`; inversion available).

### S2 — the soundness pass (Module 4) — **the heart** (see §3)
- *First file:* `Module4_SemanticAnalyzer.py` — `_validate_inductive`, invoked from `visit_Module`.
- *Exit:* negatives 5–8 rejected with distinct on-point errors; positives still pass.

### S3 — mutually-inductive groups (`inductive … with … end`)
- *First files:* `preamble.py::_emit_inductive_decls` — emit an SCC of co-defined predicates as one
  `inductive p … with q … end` group (the header already names ≥2 sigs). `Module4` positivity check
  spans the whole group (a predicate is positive across siblings too).
- *Exit:* P2 `wf`/`wf_spine` PASSES; inversion driver (3) proves `not wf(<junk>)`.

### S4 — relational + induction-via-lemma (DEPENDS ON `#@ lemma`)
- Universally-quantified consequences (`\forall x. wf(x) ⇒ P(x)`) are **not** SMT-dischargeable; they
  need the induction principle a recursive `#@ lemma` supplies (spec §6). Gate this stage on the lemma
  feature (`lemma.md`) landing. Driver: `reaches` relational demo (4) + a `wf(x) ⇒ P(x)` lemma.
- *Exit:* P3 driver PASSES end-to-end (predicate + lemma).

### S5 — reflection + docs (spec §10 P4)
- Optional reflection bridge: a recursive boolean `is_wf` + an agreement `#@ lemma`
  (`(is_wf(x)==1) == wf(x)`) for a runtime decision (spec §5/§9), gated on a driver that needs it.
  Coinductive predicates explicitly out of scope (spec §12.4).
- 5-surface doc-coherency: add `#@ inductive` (+ `#@ rule`) to `README.md`,
  `docs/pycsl-concrete-syntax-reference.md`, `docs/pycsl-static-semantics-reference.md`,
  `docs/pycsl-translational-reference.md`, `test-suite/annotations.md`, and the `pycsl-annotate` /
  `contract-writer` skill; wire `bin/doc-coherency.py --check` green.

**YAGNI exit:** stop at any stage no committed driver needs. P3/P4 (relational, reflection, coinduction)
start only on a real driver — and P3 only once `#@ lemma` exists.

---

## §3 — The soundness pass (Module 4) — detailed, because it can admit `False`

An inductive predicate is sound **iff** its defining operator is monotone, which strict positivity
guarantees (a least fixpoint then exists). Mis-enforce it and you can define `bad` with
`not bad(x) ==> bad(x)`, an inconsistent fixpoint. This pass is to inductive predicates what the
variant check is to lemmas. `_validate_inductive` enforces (each a distinct `PyCSLSemanticError`;
negatives 5–8 are the teeth):

1. **Strict positivity (§7.1, the lynchpin).** Each defined predicate may occur in rule premises only
   in *positive* position — never under `not`, never in the antecedent of a nested `==>` that flips
   polarity. Implement as a recursive polarity walk over the horn clause (start positive; `not` and the
   LHS of `==>` flip; a defined-predicate atom in a negative slot ⇒ reject). Mirrors Why3's own check
   (negative 5).
2. **Conclusion shape (§7.2).** Every rule's consequent is an application of one of the predicates
   *being defined* (to argument terms, possibly built with datatype constructors). Anything else ⇒
   reject (negative 6). Decompose `prem1 and … ==> concl` (reuse the conjunct/implication structure).
3. **Arity respected (§7.3).** Every predicate reference supplies all declared arguments — no partial
   application (negative 7).
4. **Binder/argument typing (§8).** All `forall` binders and argument terms type-check against the
   declared parameter types (reuse the contract type-checker / τ-table; datatype params are `variant`).
5. **Logic-only / executable-position ban (§7.4).** Register each predicate name in the module's
   defined-logic-symbol registry; a call from executable Python (a `def` body, not a contract/lemma) ⇒
   reject (negative 8). Premises may reference only other predicates and **pure** functions (§7.5).
6. **No `\variant`, no termination obligation (§2).** Unlike recursive functions/lemmas, an inductive
   predicate carries none — explicitly *do not* emit or require one.

Open during S2 (resolve against the P2 driver): whether the positivity walk needs the IR or can run on
the Module-3 AST (start on the AST — polarity is structural).

---

## §4 — Effort sizing (P1–P3; P4 gated)

| Stage | Scope | Size |
|---|---|---|
| **R0 pre-flight** | 8+ drivers (positives + anti-soundness twins) | ~1 day |
| **S0 surface+parse** | M1 header regex, M2 decl+grammar+transformer, M3 register | ~2–3 days |
| **S1 IR + preamble emit + Why3 spike** | `inductive_decls` IR, `_emit_inductive_decls`, ordering, confirm Why3 syntax | ~2–4 days |
| **S2 soundness pass** (the heart) | Module 4 `_validate_inductive`: positivity, conclusion-shape, arity, typing, exec-ban | ~1–1.5 weeks |
| **S3 mutual groups** | `inductive … with … end`; group-wide positivity; inversion driver | ~3–5 days |
| **S4 relational + lemma-induction** | reaches demo + `wf⇒P` lemma — **gated on `#@ lemma`** | ~3–5 days (after lemma) |
| **S5 reflection + 5-surface docs** | agreement-lemma sugar (optional), doc-coherency | ~2–3 days |

**P1–P3 total: ~3–4 weeks** (excluding the lemma dependency for P3/S4). S2 dominates and owns the
soundness risk; S1's only external unknown is the Why3-syntax spike (cheap, do first).

---

## §5 — Reference corpus additions (mandatory)

Per the reference-corpus discipline, each phase ships drivers (numbers indicative, next-free at
authoring — 0555+ since 0554 is the stateful-mixin driver):

- **0555** P1 `even` predicate, used in a contract — PASS.
- **0556** P2 `wf`/`wf_spine` mutual, proves `wf(<valid>)` — PASS.
- **0557** inversion: `not wf(JArr(JInt(2), JInt(3)))` — PASS.
- **0558** P3 `reaches` over a cyclic graph + a `#@ lemma` consequence — PASS (after lemma lands).
- **0559** non-strictly-positive rule — FAIL (rejected).
- **0560** bad conclusion shape — FAIL (rejected).
- **0561** arity mismatch / partial application — FAIL (rejected).
- **0562** inductive predicate called from executable code — FAIL (rejected).

Plus the spec §11 **erasure check** (inductive predicates vanish under extraction) and **carving
correctness** (`wf` excludes exactly the junk the collapsed `Json` admits — pairs with the involution
corpus `0542`).

---

## §6 — Decided vs still open (maps spec §12)

**Decided by this plan:**
- Inductive predicates are a module-level construct modelled like `#@ datatype` (parse→IR→preamble),
  emitted **between** datatypes and axioms; mutual groups are one `inductive … with … end`.
- Module 4 enforces positivity/shape/arity/typing/exec-ban; Why3 derives intro/inversion/induction.
- No `\variant`, no termination obligation (the key contrast with recursive functions and lemmas).

**Still open (resolve in the named phase, not blocking start):**
- **§12.1 automation ceiling** — emit a targeted "this needs the induction principle → write a `#@ lemma`"
  diagnostic when an obligation mentions an inductive atom under a `\forall`. S2/S4 ergonomics.
- **§12.2 triggers for predicate atoms** — unify with the typed-quantifier/trigger proposal.
- **§12.3 reflection sugar** — auto-generate the agreement-lemma obligation; S5, gated on a driver.
- **§12.4 coinductive predicates** — greatest-fixpoint dual; explicitly **out of scope**, a follow-on.
- **§12.5 cross-module reuse** — a shared `wf_json` theory points at theory-cloning; P4+, gated.

## §7 — Net
The spec is implementable now: Why3 has native `inductive`, and PyCSL already has the module-block
folder, the `#@ datatype` pipeline to mirror, and the preamble logic-decl slot. The three things that
turn "spec" into "code-ready" are (1) recognising `#@ inductive` is a `#@ datatype`-shaped module
construct reusing the block-folder, (2) one new preamble emitter slotted **between** datatypes and
axioms, and (3) concentrating the risk in a single **Module-4 strict-positivity pass** (§3) whose
anti-soundness drivers (5–8) prove inductive definitions cannot introduce an inconsistent fixpoint.
P3 (universally-quantified consequences) is **gated on `#@ lemma`** — the designed pair. First action:
**R0** drivers, then the S1 Why3-syntax spike, then S0→S2.
