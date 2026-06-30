# the-finishable-path.md — How PyCSL can credibly "prove itself" without breaking Ceiling A or B

**Companion to** `facing-the-facts.md` (the obstruction) and `src/self-annotate/semantic-ceiling.md` (Ceiling B in detail). This document is the constructive sequel: it accepts every finding in `facing-the-facts.md` as correct — the counts reproduce (26 `\trusted`, 66 `.get`, 25 `.to_dict`, 92 `self._*` fields), and the ceilings are structural, not missing lemmas — and asks the only question left open by it: *given that, what is the version of "PyCSL proves itself" that is actually finishable, and what does finishing it consist of?*

**One-sentence statement of the path.** Stop trying to verify the emitter's *bodies*; move LINK 3 off the Python/SMT side of the byte-diff and onto the Rocq/Why3 side, where it becomes a finite set of per-handler **coherence lemmas** against an **audited** evaluator — then make the one extensional link to the running Python (LINK 2) carry real universal force instead of corpus-sampled force.

> **Corrections applied (2026-06-30) — reconciled against the real tree.** An earlier draft of this document mis-stated several concrete facts; they are fixed inline below, and summarised here so the deltas are explicit:
> 1. **LINK 2 is `bin/extraction-byte-diff.sh`, not `bin/byte-diff-sweep.sh`.** Only the former invokes the formal emitter (the Rocq-extracted `emit_stmt_full_complete` via the OCaml driver) and diffs it against Python `_stmts_to_whyml`. `byte-diff-sweep.sh` runs *only* `src/pycsl/pycsl.py` over the corpus — it is a Python-emitter **regression** gate, not a formal-equivalence check, and never touches the formal emitter.
> 2. **LINK 2 covers 26 cases, not 624.** The formal equivalence is checked over `test-suite/extraction-byte-diff/cases.txt` (26 cases, 0 diffs). The 624 figure is the unrelated `byte-diff-sweep.sh` regression corpus.
> 3. **D1 and D2 are already partly built, not greenfield.** `src/self-annotate/pycsl-wp-spec.mlw` already ships module `PyCSL_WP_Code` (the `handle_*_code` string-emitter specs) and module `PyCSL_WP_Coherence` (`eval_whyml_stmts`/`eval_whyml_expr`, the audited axioms, and the coherence lemma `assign_code_state_coherent` + SSkip). The work is to **extend** these to the remaining arms, not create them.
> 4. **There is no `emit_F : stmt_ir → string` in the spec.** The mlw emitter specs are *string-parametric* (`handle_assign_code (lhs rhs_str indent rest_str : string)(declared : bool) : string`); the `stmt_ir`-domain emitter is the *Rocq* `emit_stmt_full_complete` over the Rocq `stmt` inductive (`Phase6L_EmitBlocks.v`), not the WhyML `#@ datatype stmt_ir`. The existing coherence lemmas are at the string level and carry a working hypothesis (`eval_whyml_expr e_val_str st = e_val`); bridging them to an `stmt_ir`-indexed emitter is real, named, unbuilt work.
> 5. **SFor coherence is already an open gap in the spec** (`pycsl-wp-spec.mlw`: "Full SFor coherence deferred to `wp_for_desugar` (open gap)"), tied to the still-open `desugar_correct`. The for/while arm is therefore *not* uniformly tractable.

---

## 1. The reframe in one diagram

`facing-the-facts.md` placed LINK 3 on the wrong side of the byte-diff. It asked the Python body to prove its own contract — which is exactly where `Any`-typed `dict.get`, `.to_dict()` reflection, and `endswith`/`rsplit`/`replace` live (Ceiling A), and where the object-language-semantics requirement lands (Ceiling B). Neither ceiling is reachable from the Python side.

But the property we actually want is *extensional*: that the **string the emitter produces**, when evaluated, performs the WP state transformation. That property does not require reasoning about the Python body at all. It requires reasoning about (a) a formal emitter (today realized as the Rocq `emit_stmt_full_complete : stmt → string`, and partially as the string-parametric `handle_*_code` specs in the mlw — there is no single `emit_F : stmt_ir → string` yet; see correction 4 and the §1 caveat) and (b) an evaluator — both of which live in the proof assistant, where there is no `Any` and no Python string algebra.

```
   Phase4_WP.v  (WP calculus, proved sound in Rocq)
        │  state-arm transformers: handle_assign, handle_seq, …
        │  (mirrored in pycsl-wp-spec.mlw as `val handle_* : … → state`)
        │
   ┌────┴──────────────── LINK 3 (RE-SITED) ────────────────┐
   │  coherence lemma, over AUDITED eval axioms:            │
   │     eval_whyml_stmts(emit_code …) st = handle_F … st   │   ← lives in WhyML/Rocq
   │  TWO real emitter artifacts (do NOT conflate):         │
   │   • mlw `handle_*_code` : STRING-parametric specs      │   ← no Any, no dict.get
   │   • Rocq `emit_stmt_full_complete` : stmt → string     │   ← over the Rocq inductive
   │  SAssign + SSkip arms: ALREADY proved in the mlw.      │
   └────┬──────────────────────────────────────────────────┘
        │
   ┌────┴──────────────── LINK 2 (STRENGTHENED) ────────────┐
   │  emit_stmt_full_complete ≡ _stmts_to_whyml (Python)   │   ← the ONLY Python touch
   │  today: bin/extraction-byte-diff.sh — 26 cases (TEST) │   ← extensional, not bodies
   │  (NB: byte-diff-sweep.sh ≠ this — it is a 624-file     │
   │   Python-emitter regression gate, no formal emitter)   │
   │  target: per-run certificate OR induction equivalence  │
   └───────────────────────────────────────────────────────┘
```

The crucial move: **LINK 3 was on the Python side and was blocked; on the Rocq side it is finite and tractable.** Ceiling A never appears because nothing in the chain type-checks a Python body. Ceiling B is confronted exactly once, honestly, in the audited `eval_whyml` axioms — not smeared across 12 handlers.

One caveat the diagram makes explicit: the WhyML coherence lemmas are stated over the **string-parametric** `handle_*_code` specs (their operands are already-rendered sub-strings, with a hypothesis tying each to the right value), while the artifact LINK 2 validates is the **`stmt_ir`-domain** Rocq `emit_stmt_full_complete`. Closing LINK 3 end-to-end therefore includes a step the original draft omitted: connecting the string-level coherence lemmas to the `stmt_ir`-indexed emitter.

---

## 2. What you already have (four assets, mis-cast as scaffolding)

| Asset | Path | Current role | Role on the finishable path |
|---|---|---|---|
| WP calculus + soundness | `src/formal-semantics/rocq/Phase4_WP.v` | formal model | source of `wp_F`, the spec each arm must meet |
| Layer-3 spec, audited links | `src/self-annotate/pycsl-wp-spec.mlw` | mirrors `Phase4_WP.v`; **already contains** `PyCSL_WP_Code` + `PyCSL_WP_Coherence` (SAssign/SSkip done) | **home of the coherence lemmas** — extend to remaining arms |
| Extraction bridge | `src/formal-semantics/rocq/Phase6L_EmitExtract.v` (+ `Phase6L_EmitBlocks.v`, `Phase6L_EmitComposition.v`) | extraction | defines / extracts `emit_stmt_full_complete : stmt → string` (the real name of "`emit_F`") |
| **LINK 2 — formal equivalence** | `bin/extraction-byte-diff.sh` over `test-suite/extraction-byte-diff/cases.txt` (**26 cases**) | the bridge `emit_stmt_full_complete ≡ _stmts_to_whyml` | to be promoted from corpus testing to per-run certificate |
| Python-emitter regression gate (NOT LINK 2) | `bin/byte-diff-sweep.sh` (624 corpus files) | stability of the *Python* emitter's output | unchanged role — it never runs the formal emitter, so it is not the extensional bridge |
| Trusted stubs | `src/self-annotate/src/module6_whyml/statements.py` | "assumed correct" | **re-discharged**: a map of audited obligations, not holes |

The `#@ datatype expr_ir / stmt_ir` declarations already in `statements.py` are a *logic-only* sketch of the input model. They are **not** the domain of the existing mlw emitter specs (which are string-parametric, §1 caveat) nor of the Rocq `emit_stmt_full_complete` (which is over the Rocq `stmt` inductive). On this path that is *fine* — they were never meant to type the Python `getattr` — but neither are they yet the `emit_F` domain; treat them as a target to be reconciled with the Rocq inductive, not as an existing formal artifact.

---

## 3. The three deliverables

### D1 — Per-handler coherence lemmas (the re-sited LINK 3) — **extend, don't create**

The coherence layer already exists for two arms. `pycsl-wp-spec.mlw` ships, in module `PyCSL_WP_Coherence`, the lemma `assign_code_state_coherent` (SAssign) and the SSkip coherence pair, over the audited `eval_whyml_stmts` axioms in the same module. The deliverable is to **extend that pattern to the remaining arms**, not to write the first one.

Note the *actual* shape of the existing lemma — it is string-parametric, not `stmt_ir`-indexed, and carries a working hypothesis:

```why3
(* what is ALREADY in pycsl-wp-spec.mlw (module PyCSL_WP_Coherence) *)
lemma assign_code_state_coherent :
  forall lhs e_val_str rest_str indent declared st e_val.
    eval_whyml_expr e_val_str st = e_val ->            (* <- the working hypothesis *)
    eval_whyml_stmts (handle_assign_code lhs e_val_str indent rest_str declared) st
    = eval_whyml_stmts rest_str (update st lhs e_val)
```

The clean form the §1 diagram sketches — `eval_whyml_stmts (emit_F s) st = wp_F s st` quantified over `s : stmt_ir` — is the *goal*, not the current state: there is no `emit_F : stmt_ir → string` in the mlw, so reaching it requires (i) introducing an `stmt_ir`-indexed emitter in WhyML (or reconciling with the Rocq `emit_stmt_full_complete`) and (ii) discharging the per-arm `eval_whyml_expr` hypotheses recursively. The state arms each lemma targets — `handle_assign`, `handle_aug_assign`, `handle_array_set`, `handle_if_branch`, `handle_return`, `handle_seq`, `handle_skip`, `handle_continue`, `handle_for_init`, `handle_while_exit` (plus the loop-checking pair `check_while_inv_entry` / `check_while_body_step`) — all already exist as `val`s. Each remaining lemma is a bounded Why3/Rocq obligation — no `Any`, no reflection, no symbolic `endswith` — the kind CompCert-style developments do every day. It is heavyweight, but *bounded and known*, which is exactly what `facing-the-facts.md` showed the body route is not.

**Open arm to flag explicitly:** the spec itself defers `SFor` — `pycsl-wp-spec.mlw` carries the marker *"Full SFor coherence deferred to `wp_for_desugar` (open gap)"*, which is in turn blocked on the still-open `desugar_correct`. So `handle_for_init`/`handle_while_exit` are **not** uniformly tractable; the for/desugar arm is a known hole, not routine.

**Honest sub-gap to name now:** the spec arms do **not** yet cover all 12 Python handlers. The emitter ships `_handle_fieldassign_stmt`, `_handle_fieldaugassign_stmt`, `_handle_critical_section_stmt`, `_handle_tuple_unpack_stmt`, `_handle_ghost_assign_stmt`, `_handle_ghost_array_set_stmt`, `_handle_array_slice_set_stmt`, `_handle_expr_stmt`, and `_handle_seq_assign` — several of which have no matching `wp_F` arm. Finishing means either (i) adding the missing arms to `Phase4_WP.v` + `pycsl-wp-spec.mlw`, or (ii) explicitly stratifying them as audited-trusted with a one-line justification each. Both are legitimate; pretending the 12 already map 1:1 to the 12 spec arms is not.

### D2 — The audited evaluator axioms (Ceiling B, confronted once) — **already started**

`eval_whyml_stmts : string → state → state` (and `eval_whyml_expr`) is **already declared and axiomatized** in `pycsl-wp-spec.mlw` module `PyCSL_WP_Coherence` — the present axioms are `assign_ref_update_semantics`, `assign_let_ref_semantics`, `assign_let_semantics`, and `skip_semantics`. The deliverable is therefore not "introduce the evaluator" but **extend the axiom set to the rest of the emitted fragment and harden its audit**, keeping it minimal and auditable:

- One axiom schema per WhyML construct the emitter actually emits (`let … = ref … in`, `<-`, sequencing `;`, `if/then/else`, `while … invariant …`, array `[…] <- …`). Nothing else.
- Each axiom carries an audit citation to the Why3 manual's stated semantics, mirroring the citation discipline already in `pycsl-wp-spec.mlw` (where every `val` cites a `Phase4_WP.v` line). Extend that discipline from "mirrors Rocq" to "mirrors Why3's documented evaluation."
- `audit-guide.md` becomes the human-readable proof that the axiom set is sound and complete *for the fragment the emitter emits* — not for all of WhyML. Scoping to the emitted fragment is what keeps this finite.

This is where trust is *relocated*, not eliminated — and saying so plainly is the point (see §6).

### D3 — Strengthen LINK 2 from testing to proof (the load-bearing step)

`bin/extraction-byte-diff.sh` checks `emit_stmt_full_complete ≡ _stmts_to_whyml` **on the 26 inputs in `test-suite/extraction-byte-diff/cases.txt`** (0 diffs). It is silent on the 27th. (Do **not** confuse this with `byte-diff-sweep.sh`, which runs only the Python emitter over 624 corpus files for regression stability and never executes the formal emitter — it is not the bridge.) That 26-case gap is the whole distance between "we tested the emitter on a sample" and "the emitter is validated." Two strengths, in increasing order:

1. **Per-run certificate (translation validation, recommended).** Wire the equivalence check into the emitter's own runtime: every compilation emits the Python string *and* `emit_F` on the same `stmt_ir`, and a small checked comparator asserts equality for *that* run. Now each individual proof PyCSL produces is accompanied by a certificate that the codegen step that produced it matched the validated formal emitter — Necula-style certifying compilation. The TCB shrinks to the comparator (tiny, auditable) plus D2. This is genuinely finishable by extending the `bin/extraction-byte-diff*.sh` machinery (which already builds and runs the extracted `emit_stmt_full_complete` driver) into a per-run comparator — **not** `byte-diff-sweep.sh`, which has no formal emitter to compare against.

2. **Induction equivalence (research-grade).** Prove `forall s. emit_F s = model_of_python_emitter s` by structural induction, where `model_of_python_emitter` faithfully captures the Python recursion pattern. Stronger, universal, and much harder; only worth it if the per-run certificate proves insufficient for the claim you want to publish.

Ship #1. Treat #2 as optional.

---

## 4. Worked micro-example: `handle_assign`

**Reality check first.** This arm is **already implemented** in `pycsl-wp-spec.mlw`: the emitter spec is `handle_assign_code` (module `PyCSL_WP_Code`), the evaluator axioms are `assign_*_semantics`, and the coherence lemma is `assign_code_state_coherent` (module `PyCSL_WP_Coherence`). The snippet below is the *idealized `stmt_ir`-indexed shape* the path aims at — useful for seeing the destination, but it is **not** what is in the tree, and the differences are exactly the unbuilt work:

```why3
(* IDEALIZED (aspirational) — a TOTAL emitter over stmt_ir, in WhyML.
   NB: no such `emit_assign : ident → expr_ir → string` exists today; the
   shipped spec `handle_assign_code` is STRING-parametric (operands already
   rendered). Introducing this stmt_ir form is part of D1's remaining work. *)
function emit_assign (x: ident) (e: expr_ir) : string =
  "let " ^ x ^ " = ref " ^ emit_expr e ^ " in\n"

(* D2: audited evaluator axiom for the let-ref form (cited to Why3 semantics).
   The shipped analogue is `assign_let_ref_semantics`, stated over strings. *)
axiom eval_let_ref :
  forall x e st.
    eval_whyml_stmts (emit_assign x e) st = M.set st x (VInt (eval_expr st e))

(* D1: the coherence lemma. The shipped `assign_code_state_coherent` is NOT a
   one-liner — it is string-parametric and carries the hypothesis
   `eval_whyml_expr e_val_str st = e_val`. Reaching this clean stmt_ir form
   means discharging that hypothesis recursively via `emit_expr`. *)
lemma handle_assign_coherent :
  forall x e st.
    eval_whyml_stmts (emit_assign x e) st = update st x (eval_expr st e)
```

The Python `_handle_assign_stmt` is **never touched here**. It stays `\trusted` in `statements.py` — but its annotation comment changes from *assumed correct by inspection* to:

```python
#@ \trusted reviewer: pycsl-self-annotate
#@ validated-by: LINK2 per-run certificate (emit_assign) + lemma handle_assign_coherent
#@ requires True
#@ ensures True
#@ assigns \nothing
```

Same stub, different epistemic status. Repeat across the arms and the `\trusted` markers stop being a map of holes and become a **map of audited, discharged obligations**. *That* is what "finish the annotation so it can prove itself" actually produces — not body-faithful `ensures` clauses the SMT backend can never discharge.

---

## 5. Order of work

1. **Re-discharge the stubs (cheap, do first).** Replace every `requires True / ensures True` justification comment in `statements.py` with a `validated-by:` line pointing at its intended LINK2 artifact + coherence lemma — even before those exist. This converts the document `facing-the-facts.md` into an actionable obligation list and prevents the stubs from reading as laziness.
2. **Close the arm-coverage gap (D1 scoping).** For each of the 12 `_handle_*` methods, decide: matched spec arm, new spec arm to add, or explicitly audited-trusted. Write the table. This is the honest core of "finishing the annotation."
3. **Extend + audit the evaluator axioms (D2).** Build on the existing `PyCSL_WP_Coherence` axioms (`assign_*_semantics`, `skip_semantics`); add one per remaining emitted construct, scope `eval_whyml_stmts` to that fragment, cite each axiom, finish `audit-guide.md`.
4. **Extend the coherence lemmas (D1).** SAssign (`assign_code_state_coherent`) and SSkip are already proved; continue with `handle_seq`, `handle_return` — the two that compose everything else — then the rest, deferring `SFor`/`wp_for_desugar` as the known open gap.
5. **Ship the per-run certificate (D3 #1)** by extending `bin/extraction-byte-diff*.sh` (the scripts that already build/run the extracted `emit_stmt_full_complete` driver) into a runtime comparator. *(Not `byte-diff-sweep.sh` — it has no formal emitter.)*

Steps 1–2 are days. Steps 3–4 are the real cost, but bounded and standard. Step 5 reuses existing scripts.

---

## 6. What "proves itself" then means — and the limit it respects

The end state is a defensible, writeable claim:

> The PyCSL emitter is correct **relative to** an audited model of WhyML evaluation, **validated per-output** against the running Python emitter.

Residual TCB = (a) the `eval_whyml_stmts` axioms (D2, audited), (b) the per-run comparator (D3, tiny), (c) any handler explicitly stratified as audited-trusted (D1 sub-gap). Everything else is machine-checked.

This deliberately does **not** claim the thing `facing-the-facts.md`'s Gödel/Löb row already rules out: a from-nothing, zero-audited-axiom proof of the generator by the system itself. That target is not merely hard, it is unreachable in principle, so it was never the finish line. The finish line is **shrinking and exposing the TCB** until what remains is a short, audited, human-checkable axiom set plus a trivial comparator. "Facing the facts" is the correct posture; this document is what facing them and then continuing looks like.

---

## 7. Reproduce / check the path's premises

```bash
cd <repo-root>

# (A) The state arms the spec already declares (targets for D1):
grep -oE 'val handle_[a-z_]+' src/self-annotate/pycsl-wp-spec.mlw | sort -u

# (A') The coherence work ALREADY done (D1/D2 are not greenfield):
grep -nE 'module PyCSL_WP_(Code|Coherence)|eval_whyml_stmts|assign_code_state_coherent|_semantics' \
    src/self-annotate/pycsl-wp-spec.mlw | head

# (B) The handlers needing arm-coverage decisions (D1 sub-gap, §3):
grep -oE 'def _handle_[a-z_]+' src/pycsl/module6_whyml/statements.py | sort -u

# (C) LINK 2 is bin/extraction-byte-diff.sh over 26 cases (NOT byte-diff-sweep):
grep -vcE '^\s*#|^\s*$' test-suite/extraction-byte-diff/cases.txt   # -> 26
bash bin/extraction-byte-diff.sh   # builds emit_stmt_full_complete, diffs vs Python; silent on case 27
#   (byte-diff-sweep.sh is the 624-file PYTHON-emitter regression gate — no formal emitter)
grep -nE 'pycsl\.py|extract|rocq|ocaml|formal' bin/byte-diff-sweep.sh   # -> only pycsl.py

# (D) The trust to be re-discharged, not removed (§4):
grep -c '#@ .trusted' src/self-annotate/src/module6_whyml/statements.py   # 26
```

---

## 8. Bottom line

`facing-the-facts.md` proved that LINK 3, *as placed*, is blocked — the Python emitter body cannot be verified against a non-trivial contract by an SMT-backed Hoare verifier, because that asks one tool to be a verified compiler, a string solver, a dynamic-data refinement system, and a metacircular reflector at once. The finishable path does not contest any of that. It **moves LINK 3 to the other side of the byte-diff**, where it decomposes into a finite set of coherence lemmas over an audited evaluator, and **upgrades LINK 2** from corpus testing to a per-run certificate so the one extensional link to the running Python carries real force. The result is not "PyCSL bootstraps its own soundness from nothing" — that is provably unattainable — but "PyCSL's emitter is machine-checked correct modulo a short, audited object-language axiom set, certified per output." That is the strongest claim the facts permit, and unlike the body sweep, every step of it is bounded, named, and buildable from assets already in the tree.
