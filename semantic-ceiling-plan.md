# semantic-ceiling-plan.md — A plan to break the semantic ceiling

> **What this plans.** How to make the 12 `_handle_*` emitter methods (in
> `module6_whyml/statements.py`) verify **body-faithful** — i.e. strip `\trusted`
> and prove each against a real contract — by defeating the *semantic ceiling*
> that `facing-the-facts.md` and `src/self-annotate/semantic-ceiling.md`
> identified. Self-contained; grounded in the measured state of those two docs
> and the Phase-A/B typed-IR migration (`ir-schema-spec.md`).
>
> **Convention.** Named repo-root plan file. New capability ⇒ reference-corpus
> additions (WI-C7). Leaf-first (`feedback_leaf_first`): fix leaf functions with
> correct value contracts before composite ones. Faithful semantics
> (`feedback_no_more_int`): lower each Python type to its faithful WhyML class,
> never coerce to `int`.

---

## 0. The honest framing — there are two ceilings, and only one is "breakable"

`facing-the-facts.md §3.1` splits the wall in two. This plan treats them
differently because their reducibility differs:

- **Ceiling A — modeling / expressiveness.** The bodies use operations with no
  faithful WhyML lowering: `.to_dict()` reflection, `Any`-typed `dict.get` +
  runtime-tag dispatch, `str.endswith / rsplit / strip / replace / decode`,
  `stable_hash`, and mutation of a ~92-field transpiler state. This is *why the
  body cannot be type-checked or framed once un-`\trusted`*, independent of any
  contract. **Ceiling A is an engineering problem. It is breakable.**

- **Ceiling B — semantic adequacy (metacircular).** Even a body proved against a
  *string-shape* postcondition (`\result = indent ^ "let " ^ lhs ^ …`) does not
  prove the property we want — that the emitted WhyML, *when evaluated*, performs
  the WP state transformation. Closing that needs an in-logic model
  `eval_whyml : string → state → state` of the object language. By Gödel/Löb a
  system cannot fully prove the soundness of its own evaluator. **Ceiling B is
  NOT eliminable — only stratifiable** into an audited evaluator axiom (this is
  exactly the D2 boundary the coherence route already uses,
  `src/self-annotate/evaluator-axiom-audit.md`).

**Thesis of this plan.** *Break Ceiling A outright; reduce Ceiling B to the single
already-accepted audited evaluator axiom by connecting each body-faithful
string-contract to the per-arm coherence lemma that already exists in
`pycsl-wp-spec.mlw`.* The residual trust after this plan is **one audited axiom
per construct** (the same the coherence route already banks), not a `\trusted`
method body. That is what "breaking the ceiling" concretely means here — not
metacircular omniscience, which is provably unavailable.

**Two levers we already hold (do not re-derive):**
1. **Phase A/B is the "Json-ADT rewrite", already done in the real code.** The
   dreaded `Dict[str,Any]` + tag-dispatch has *already* been replaced by typed
   `StmtIR`/`ExprIR` sums that Module 6 consumes (`ir-schema-spec.md §10`,
   624-file byte-diff clean). So Ceiling A's "dynamically-typed data" sub-problem
   is 80 % solved at the value level; the residue is bodies that still
   *round-trip through `.to_dict()`* and the string/state ops.
2. **The coherence lemmas already stratify Ceiling B.** `pycsl-wp-spec.mlw`
   proves, per WP arm, `eval_whyml_stmts (handle_X_code …) st = wp_X … st` from an
   atomic `X_semantics` axiom. A body-faithful `ensures \result == <the exact
   string>` is the *missing premise* that feeds those lemmas from the
   implementation side.

---

## 1. Objective & success criterion

**Objective.** For each `_handle_*` method, replace `\trusted` with a proved
`ensures \result == <the WhyML string it emits>` (+ a sound `assigns`), such that
composing it with the existing per-arm coherence lemma discharges that arm's
`module6_encodes_mlw` obligation — down to the audited evaluator axiom.

**"Broken" =** every `_handle_*` in buckets 1–2 (leaf + compositional, §the
ir-schema buckets) is body-faithful; bucket-3 methods have a *named, modeled*
residual (state-record / sibling-contract) rather than an opaque `\trusted`; and
the only remaining trust is the enumerated evaluator axioms (D2) — **0 new axioms
beyond those**, both provers still green, byte-diff still 26/26.

---

## 2. Breaking Ceiling A — the five modeling gaps

Each gap: the operation, the faithful model, and the **preferred move
(eliminate > model)**.

### A1 — Reflective dict (`.to_dict()` + `dict.get` + tag dispatch)
**Preferred: ELIMINATE.** The bodies still call `stmt.value.to_dict()` and then
`dict.get(...)` even though `stmt` is now a typed `StmtIR`. Refactor each body to
read **typed fields directly** (`stmt.target`, `stmt.value` as `ExprIR`), deleting
the `.to_dict()` round-trip. This is a *real code change to the emitter*, gated
byte-identical. Where data is *genuinely* heterogeneous (rare, e.g. an untyped
metadata bag), model a small **`Json`/`Dynamic` universal ADT** in the
self-annotate model and rewrite that one consumer as a total `match`. Prefer
elimination; only model the irreducible residue.

### A2 — String-builder operations
The bodies build WhyML with `f"…"`, `^`-concat, and content queries
(`endswith / rsplit / strip / replace / decode`) + `stable_hash`.
- **f-string (all-string):** already lowered to real `str_concat` (B2, fixed).
  Extend to the *mixed* case only as needed.
- **`endswith / startswith / strip / replace / rsplit`:** model each as a faithful
  `string.String`-theory operation, or add it as a **trusted string primitive**
  with an audited spec (a small, enumerable extension of the string model —
  `feedback_no_more_int` compliant). These are the "custom string decision
  procedure" corner of `facing-the-facts.md §7`; keep the trusted surface tiny and
  listed.
- **`stable_hash` (gensym):** it is only used to mint fresh names. Model it as an
  **abstract injective `int → string`** (or replace the call with the existing
  `self._havoc_counter`), so freshness is a `∀ i≠j. h i ≠ h j` audited fact, not a
  hash computation.

### A3 — Transpiler-state mutation (the ~92 fields)
**Model the state as a record.** The emitter mutates `self._dict_locals`,
`self._add_abstract_op(...)`, `self._havoc_counter`, etc. Introduce a
**transpiler-state record** (the fields each method actually touches) so
`#@ assigns self._dict_locals, self._abstract_ops, …` is *soundly stateable* and
provable. Leaf-first: model only the fields a given method touches. This is the
`assigns`-framing half of Ceiling A.

### A4 — Trusted sibling returns (`_expr_to_whyml`, `_stmts_to_whyml`)
**Leaf-first (the doctrine).** These recursive siblings are the *leaves* of the
emitter. Give them real **value contracts** first
(`ensures \result == <string>` for the shapes they emit, or a coherence-carrying
`ensures`), so a composite `_handle_if_stmt` that concatenates their results can
prove its own string contract. Fix the leaves' VALUE contracts before the
top-level (`feedback_leaf_first`); this is the crux that turns "depends on an
unmodeled return" into "depends on a proved return".

### A5 — Result: bodies become string-faithful
After A1–A4, each `_handle_*` body is typed field access + faithful string ops +
framed state effects → its `ensures \result == <exact WhyML string>` is provable.
**Ceiling A is broken for that method.**

---

## 3. Reducing Ceiling B — connect to the coherence lemmas (not eliminate)

Ceiling B is not solved by A. But it is **already stratified**: `pycsl-wp-spec.mlw`
proves `X_code_state_coherent : eval_whyml_stmts (handle_X_code …) st = wp_X … st`
from the atomic audited axiom `X_semantics`. The one missing link is a *proof from
the implementation side* that the Python `_handle_X` actually emits
`handle_X_code …`. That link **is** the body-faithful `ensures` from §2.

So the pipeline per arm becomes:

```
_handle_X body  ──(A1–A4, body-faithful)──►  ensures \result == handle_X_code(...)
                                                    │
                                                    ▼  (existing, proved in pycsl-wp-spec.mlw)
                          X_code_state_coherent : eval_whyml_stmts(handle_X_code …) = wp_X …
                                                    │
                                                    ▼  residual trust
                                   audited evaluator axiom  X_semantics   (D2, enumerated)
```

**What this buys:** the emitter method is no longer `\trusted`; its correctness
reduces to (i) a proved string-shape contract (Ceiling A, broken) + (ii) a proved
coherence lemma (already done) + (iii) one audited evaluator axiom per construct
(the pre-existing D2 boundary). No *new* trust is introduced — the `\trusted`
method body is *replaced* by an already-banked audited axiom. That is the maximal
"break" Gödel/Löb permits.

---

## 4. Work items

| WI | Item | Ceiling | Gate |
|---|---|---|---|
| **C1** | Eliminate `.to_dict()` round-trips in the leaf handlers; read typed `StmtIR`/`ExprIR` fields (real emitter refactor) | A1 | byte-diff 0 |
| **C2** | Faithful string-op model: `endswith/startswith/strip/replace/rsplit` as `string.String` ops or enumerated trusted primitives; `stable_hash`→injective/counter | A2 | ops have audited specs; byte-diff 0 |
| **C3** | Transpiler-state record model; per-method `assigns` frames (leaf-first, only touched fields) | A3 | frame soundly stated + proved |
| **C4** | Value contracts for the leaf siblings `_expr_to_whyml` / `_stmts_to_whyml` (the recursion leaves) | A4 | leaf `ensures \result == …` proves |
| **C5** | Body-faithful `ensures \result == handle_X_code(...)` for each **leaf** `_handle_*` (pass/return/continue/assign/arrset) | A5 | self-annotate proves; un-`\trusted` |
| **C6** | Body-faithful for the **compositional** handlers (if/seq/while/for), reusing C4 leaves | A5 | proves; un-`\trusted` |
| **C7** | Connect each body-faithful `ensures` to its `*_code_state_coherent` lemma → discharge the per-arm `module6_encodes_mlw` from the implementation side | B | Print Assumptions: only D2 axioms |
| **C8** | Reference corpus + non-vacuity: a false `ensures \result == "wrong"` must FAIL for each converted handler | — | corpus clean; false-shape fails |
| **C9** | Bucket-3 residue (`try/match/slice-set/critical`): named modeled residual (state-record + sibling contracts), not opaque `\trusted` | A3/A4 | residual enumerated, not silent |
| **C10** | Docs: update `semantic-ceiling.md`, `facing-the-facts.md`, `ir-schema-spec.md §10/§11`, `arm-coverage.md` to record which methods crossed Ceiling A and the residual trust | — | docs reconciled |

---

## 5. Sequencing (leaf-first, thinnest vertical slice first)

```
Slice 0 (prove the route on ONE arm):  C1+C2+C3+C4+C5 for `_handle_assign_stmt` only,
                                        then C7 connect to assign_code_state_coherent.
                                        ⇒ one arm fully body-faithful, residual = 1 audited axiom.
Slice 1 (leaves):   remaining leaf handlers (pass/return/continue/arrset)     [C5]
Slice 2 (leaves↑):  sibling value contracts _expr_to_whyml/_stmts_to_whyml    [C4]
Slice 3 (compose):  if/seq/while/for on top of the proved leaves             [C6]
Slice 4 (connect):  C7 for every converted arm; Print Assumptions audit
Slice 5 (residue):  bucket-3 modeled residual [C9]; corpus + non-vacuity [C8]; docs [C10]
```

**Rationale.** Slice 0 is the *proof of concept that the ceiling is broken* for a
single construct end-to-end (Ceiling A cleared + Ceiling B connected to the
existing lemma). If Slice 0 does not close, the plan is falsified cheaply and we
fall back to §8. Everything after Slice 0 is repetition + composition.

---

## 6. Gate criteria (per converted method, and overall)

1. **Byte-identical** across the extraction/byte-diff sweep after every emitter
   refactor (`bin/byte-diff-sweep.sh`, parallel; `feedback_parallel_sweep`).
2. **Self-annotate proves** the method body-faithful (`pycsl` on the mirror), and
   the method is **no longer `\trusted`** (`self-annotate-mirror-check.sh`).
3. **No NEW trust.** `Print Assumptions` / the arm-coverage audit shows the
   residual is only the enumerated D2 evaluator axioms + the tiny listed string
   primitives (C2) — nothing else. A converted method adds **0** opaque trust.
4. **Non-vacuity (C8):** a deliberately wrong `ensures \result == "…"` FAILS, so
   the body-faithful contract is not vacuously satisfied.
5. **Reference corpus:** a `pycsl-reference` case exercising each converted
   construct stays Valid (`feedback_reference_corpus`).

---

## 7. Non-goals / accepted residual (honest)

- **Full elimination of Ceiling B is a NON-GOAL** — impossible (Gödel/Löb). The
  target is *stratification into the already-audited evaluator axioms*, not their
  removal. If a plan claims to remove them, it is wrong.
- **A general `Json`/`Dynamic` universal ADT with every consumer rewritten** is a
  fallback for genuinely heterogeneous residue only (A1). Prefer elimination via
  the typed `StmtIR`; a full universal-ADT rewrite "is a different program"
  (`facing-the-facts.md §4`) and re-incurs Ceiling B per arm — avoid unless forced.
- **The transpiler I/O, CLI, libcst visitors** stay out of model (they are not WP
  arms; `formal-semantics-completion.md §5`).
- **Content-semantic string reasoning beyond the enumerated primitives** (e.g.
  proving a `replace` chain computes a specific normalization) is out of scope —
  keep the string surface small and audited (C2).

---

## 8. Fallback if the direct route stalls (from `facing-the-facts.md §7`)

If Slice 0 shows the per-method modeling cost is prohibitive, switch to the
literature's realistic alternatives, in preference order — these do **not** verify
the generator but achieve equivalent assurance:

1. **Proof-producing / certifying emission** (Myreen-style): make `_handle_*`
   emit a *proof/witness alongside* the WhyML, so the generator need not be
   verified — the per-compile certificate discharges the obligation. We already
   have the skeleton (`bin/per-run-certificate.sh`); upgrade it from byte-diff to a
   *semantic* per-run certificate (each compile emits the coherence instance for
   the arms it used).
2. **Translation validation** (Pnueli–Siegel–Singerman / seL4 binary validation):
   validate *this output* semantically (not byte-diff) against the WP model per
   run. Needs the same object-language model (Ceiling B) but only *per output*,
   not for all inputs — strictly weaker and often tractable.
3. **Stratified trust as-is:** keep the emitter `\trusted` but maximize the
   coverage of the Why3-side coherence lemmas (the current re-sited LINK 3), and
   treat this plan's Ceiling-A work as *optional hardening*.

The fallback is not defeat — it is the state-of-the-art answer to "verify a
string-producing, reflective, large-state metaprogram", which no single
SMT-backed Hoare verifier does head-on.

---

## 9. The smallest first experiment (Slice 0, concretely)

Target: **`_handle_assign_stmt`**, the arm `semantic-ceiling.md` itself uses as the
running example, and which already has a proved `assign_code_state_coherent`
lemma.

1. **C1:** delete any `.to_dict()` in its body; read `stmt.target : str`,
   `stmt.value : ExprIR`. Byte-diff 0.
2. **C4:** give `_expr_to_whyml` a value contract for the shapes `assign` needs
   (int/var/binop leaves).
3. **C2/C3:** the two emitted shapes are `let {t} = ref {v} in\n{rest}` and
   `{t} := {v};\n{rest}` — pure `^`-concatenation of typed fields + one
   `declared_refs` membership test; frame `assigns declared_refs`.
4. **C5:** prove
   `ensures \result == indent ^ "let " ^ target ^ " = ref " ^ rhs ^ " in\n" ^ rest`
   (and the ref-update branch), un-`\trusted` the method.
5. **C7:** feed that `ensures` into `assign_code_state_coherent` to discharge the
   assign arm of `module6_encodes_mlw` from the implementation side; `Print
   Assumptions` must show only `assign_semantics` (a D2 axiom).
6. **C8:** confirm a wrong `ensures` FAILS.

If steps 1–6 close, the semantic ceiling is **broken for one arm end-to-end**, and
the residual trust for that arm is exactly one enumerated evaluator axiom — the
plan is validated and Slices 1–5 are its systematic repetition. If step 3 or 5
proves intractable (e.g. the string ops resist a faithful model), that is the
precise, early signal to take §8's fallback.
