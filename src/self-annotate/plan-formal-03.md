# plan-formal-03 — Closing the Remaining Layer 1/3 Gaps

**Follows:** `plan-formal-02.md` (ghost tags + `PyCSL_WP_Code` for 9 WP arms complete)
**Companion:** `semantic-ceiling.md`, `pycsl-wp-spec.mlw`, `audit-guide.md`, `coverage-report.md`

---

## 1. What plan-formal-02 Achieved

| Item | Status |
|---|---|
| Ghost output tags for 9 remaining WP handlers (rocq/ + lean/ + src/) | Done — 37 new `#@` per file, all pass `pycsl --no-proof` |
| `PyCSL_WP_Code` — 9 `val function` string specs (SAssign was pre-existing) | Done |
| `PyCSL_WP_Coherence` — 5 Z3-proved coherence lemmas | Done |
| `PyCSL_WP_Coherence` — 4 human-audited coherence axioms | Done |
| coverage-report.md updated | Done |

**All 10 WP arms (SFor as placeholder)** now have:
- Layer 1 ghost output tags proving dispatch exhaustiveness
- Layer 3 string-level specification in `PyCSL_WP_Code`
- Layer 3 coherence proof or human-audited axiom in `PyCSL_WP_Coherence`

**Remaining gaps** (in priority order):

1. `desugar_correct` proof closes the SFor gap (24–33h, high formal value)
2. Strengthening the 4 human-audited coherence axioms to machine-checked lemmas
3. Audit-guide.md checklist pass
4. CI integration (`make self-annotate` target)

---

## 2. Recommendations

### Priority 1 — Prove `desugar_correct` in Rocq and Lean (~24–33h)

Do nor forget to load skill `lean` and `rocq` under `config/skills`.

`desugar_correct` is the only `Admitted`/`sorry` in the formal proofs. It states that
desugaring a `for` loop into a `while` loop is semantically equivalent:

```coq
(* Phase3b_Desugar.v *)
Theorem desugar_correct : forall x iter inv var body st Q,
  wp (SFor x iter inv var body) Q st <->
  wp (desugar x iter inv var body) Q st.
Admitted.
```

Once proved, `_handle_for_stmt` can have a proper Layer B contract and the SFor
arm can be added to `PyCSL_WP_Code` + `PyCSL_WP_Coherence`.

**Effort:** 24–33h.
**Why first:** closes the only formal gap where a proof obligation exists but is
not met. All other open gaps are about strengthening already-correct specs.

**Sub-steps:**
1. State the desugar lemma over the operational semantics (Phase3_SOS.v)
2. Prove loop-index initialization: `st ⊢ let _idx = ref 0 in ...` is equivalent to the for semantics
3. Prove index-bound preservation: the while condition mirrors the for iteration range
4. Assemble `desugar_correct` from the sub-lemmas
5. Mirror to Lean4 (`Phase3b_Desugar.lean`)
6. Update `_handle_for_stmt` contract: add `#@ requires \length(iter) >= 0` and strengthen `ensures`

### Priority 2 — Strengthen the 4 human-audited coherence axioms (~3h)

The following axioms in `PyCSL_WP_Coherence` are currently human-audited (not
machine-checked) because Z3 times out or returns Unknown on their disjunction
case-splits:

| Axiom | Blocker | Approach |
|-------|---------|---------|
| `skip_code_state_coherent` | Z3 Unknown on `skip_code` disjunction | Split `handle_skip_code` into `handle_skip_with_rest` + `handle_skip_norest` and prove each half separately |
| `array_set_code_state_coherent` | Z3 Timeout on match + string concat | Use `--steps 1000000` or switch to Alt-Ergo with induction on string structure |
| `seq_code_state_coherent` | Z3 Timeout on `handle_seq_code` disjunction | Same split strategy: `handle_seq_with_semi` + `handle_seq_concat` |
| `return_plain_code_state_coherent` | Z3 Timeout on string concatenation | Add intermediate let-binding: `let code_str = handle_return_code ...` then case split |

**Split strategy (recommended for skip and seq):**

```why3
(* Replace: val function handle_skip_code (indent rest_str : string) : string
 *           ensures { result = ... \/ result = ... }
 *
 * With two simpler functions: *)
val function handle_skip_with_rest (indent rest_str : string) : string
  ensures { result = indent ^ "()" ^ ";\n" ^ rest_str }

val function handle_skip_norest (indent : string) : string
  ensures { result = indent ^ "()" }
```

Each half has a single `ensures` clause (no disjunction) and Z3 can discharge
the coherence lemma in a single step.

**Effort:** ~3h for all 4 axioms.

### Priority 3 — Audit-guide.md checklist (~1h)

`audit-guide.md` defines the human-audit checklist that validates the link
between the Rocq/Lean definitions and the Layer 3 val specs. Run through the
checklist for each of the 9 new `val function` specs added in plan-formal-02
(SSkip through SContinue) and add the audit trail entries.

The checklist items per `val function` are:
1. The formal correspondent is cited (Rocq file + line numbers)
2. The ensures clause mirrors the Rocq definition by inspection
3. The WhyML types are consistent with `Phase2_State.v` type definitions
4. Any disjunction in the ensures is exhaustive (all branches are covered)

**Effort:** ~1h (9 specs × ~7min each).

### Priority 4 — CI integration (~30min)

Add the Layer 1 and Layer 3 verification commands to the Makefile:

```makefile
self-annotate-verify:
	@source .venv/bin/activate && \
	for path in rocq lean src; do \
	    python3 src/pycsl/pycsl.py --no-proof \
	        src/self-annotate/$$path/Module6_WhyMLTranspiler.py || exit 1; \
	done
	@why3 prove src/self-annotate/pycsl-wp-spec.mlw -P "Z3,4.13.3," || exit 1
	@echo "Layer 1 + Layer 3 verification PASS"
```

This makes `make self-annotate-verify` the single command to confirm the full
L1→L3 bridge is intact after any change to the annotated files or the spec.

---

## 3. The SFor Sub-Plan (Priority 1 Detail)

### 3.1 Current State

```coq
(* Phase3b_Desugar.v:73-81 *)
Fixpoint desugar (x : ident) (iter_var : ident) (inv : contract_expr)
    (var : contract_expr) (body : list stmt) : list stmt :=
  [ SAssign "_idx" (EInt 0);
    SWhile inv var (EBinOp Lt (EVar "_idx") (ECall "len" [EVar iter_var]))
      (SSeq (SAssign x (ECall "get" [EVar iter_var; EVar "_idx"]))
            (SSeq (SAppend body)
                  (SAugAssign "_idx" Add (EInt 1)))) ].

Theorem desugar_correct : forall x iter inv var body st Q, ...
Admitted.
```

### 3.2 Proof Strategy

The proof proceeds by strong induction on the number of iterations.

**Base case:** When `eval_bool st (EBinOp Lt (EVar "_idx") ...)` is false at
entry (loop body never executes), both `wp (SFor ...)` and `wp (desugar ...)`
reduce to `Q st`.

**Inductive step:** Assume the equivalence holds for `n` iterations. Show it
holds for `n+1`. The key lemma needed is `SAssign_subst`:
```coq
Lemma SAssign_subst : forall x e σ Q,
  wp (SAssign x e) Q σ = Q (update σ x (eval_expr σ e)).
```
which follows directly from the SAssign WP rule.

**Index arithmetic:** The loop index `_idx` is initialized to 0 and incremented
exactly once per iteration. The bound `eval_expr σ (ECall "len" [EVar iter_var])`
is stable across iterations (the list is not mutated by body — this requires
`assigns` analysis, which is available from the SemanticAnalyzer).

### 3.3 Files to Modify

| File | Change |
|------|--------|
| `src/formal-semantics/rocq/Phase3b_Desugar.v` | Remove `Admitted`; add full proof |
| `src/formal-semantics/lean/PyCSL/Phase3b_Desugar.lean` | Remove `sorry`; add full proof |
| `src/self-annotate/rocq/Module6_WhyMLTranspiler.py` | Strengthen `_handle_for_stmt` contract: `requires iter_len >= 0`, `ensures _for_form == 1` |
| `src/self-annotate/lean/Module6_WhyMLTranspiler.py` | Same |
| `src/self-annotate/src/Module6_WhyMLTranspiler.py` | Same |
| `src/self-annotate/pycsl-wp-spec.mlw` | Add `handle_for_code` val to `PyCSL_WP_Code`; add `for_code_state_coherent` to `PyCSL_WP_Coherence` |
| `src/self-annotate/coverage-report.md` | Update SFor row from "blocked" to "proved" |

---

## 4. Verification After Priority 1

```bash
# Rocq: verify desugar_correct proof compiles
cd src/formal-semantics/rocq
rocq compile Phase3b_Desugar.v

# Lean: verify desugar_correct proof compiles
cd src/formal-semantics/lean
lake build

# Layer 1: _handle_for_stmt with strengthened contract
source .venv/bin/activate
python3 src/pycsl/pycsl.py --no-proof \
    src/self-annotate/rocq/Module6_WhyMLTranspiler.py

# Layer 3: SFor string spec and coherence lemma
why3 prove src/self-annotate/pycsl-wp-spec.mlw -P "Z3,4.13.3,"
```

---

## 5. Effort Summary

| Task | Priority | Effort | Risk |
|------|----------|--------|------|
| `desugar_correct` (Rocq + Lean) | 1 | 24–33h | High (complex inductive proof) |
| Strengthen 4 human-audited axioms | 2 | 3h | Low (val function split) |
| Audit-guide.md checklist | 3 | 1h | Low |
| CI integration | 4 | 30min | Low |
| **Total (P2–P4 only)** | | **~4.5h** | |
| **Total (all)** | | **~28–38h** | |

**Recommended next session:** tackle Priority 2 (split strategy for
`handle_skip_code` and `handle_seq_code`). This is a mechanical 3h task
with no formal proof risk, and elevates 4 human-audited axioms to
machine-checked lemmas, improving the trust chain.

---

Once the plan is done, provide recommendations and draft a new plan in `./src/self-annotate/plan-formal-??.md` where ?? is a new number compared to existing ones.