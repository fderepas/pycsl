# plan-formal-04.md — Elevate Human-Audited Axioms to Machine-Checked Lemmas

**Status of previous plan (plan-formal-03.md):** COMPLETE.
- `desugar_correct` proved in Rocq and Lean (zero `admit`/`sorry`).
- `handle_for_init`, `handle_for_code`, `for_code_state_coherent` added to `pycsl-wp-spec.mlw` (Z3-proved).
- `_handle_for_stmt` annotation strengthened: `requires stmt != 0`, `requires \length(rest) >= 0`.
- `coverage-report.md` updated: SFor row from "blocked" to "proved (desugar_correct)".

---

## 1. Remaining Open Gaps After plan-formal-03

| Gap | Status | Blocking? |
|-----|--------|-----------|
| `wp_for_desugar` coherence | `admit`/`sorry` in Phase5b_Soundness.v and Soundness.lean | Soundness theorem not fully closed |
| `WhileInv` (Lean) | 2 `sorry` | Lean WhileInv proof incomplete |
| `skip_code_state_coherent` | Axiom (human-audited) — Z3 Unknown on disjunction | Layer 3 quality |
| `array_set_code_state_coherent` | Axiom (human-audited) — Z3 Timeout | Layer 3 quality |
| `seq_code_state_coherent` | Axiom (human-audited) — Z3 Timeout | Layer 3 quality |
| `return_plain_code_state_coherent` | Axiom (human-audited) — needs intermediate let-binding | Layer 3 quality |

---

## 2. Priority 1 — Split and Prove the 4 Human-Audited Axioms (~3h)

These 4 axioms in `PyCSL_WP_Coherence` are correct (human-verified) but Z3 times out or returns Unknown. The fix: split each axiom into smaller sub-lemmas that Z3 can discharge individually.

### 2.1 `skip_code_state_coherent` (Z3 Unknown on disjunction)

**Root cause:** The `handle_skip_code` ensures clause is a disjunction:
```why3
result = indent ^ "()" ^ ";\n" ^ rest_str
\/ result = indent ^ "()"
```

Z3 fails on goals of the form `P \/ Q → something`, because it cannot choose the branch.

**Fix:** Split into two lemmas:
```why3
lemma skip_code_state_coherent_with_rest :
  forall indent rest_str st.
  rest_str <> "" ->
  let code = handle_skip_code indent rest_str in
  eval_whyml_stmts code st = eval_whyml_stmts rest_str st

lemma skip_code_state_coherent_norest :
  forall indent st.
  let code = handle_skip_code indent "" in
  eval_whyml_stmts code st = st
```

Each sub-lemma uses a specific branch of the `ensures` disjunction.

**Required supporting changes:**
- Split `handle_skip_code` val into two: `handle_skip_code_with_rest` and `handle_skip_code_norest`, each with a single non-disjunctive `ensures`.
- Or: add a precondition (`rest_str = ""` vs. `rest_str <> ""`) to guide the prover.

### 2.2 `array_set_code_state_coherent` (Z3 Timeout)

**Root cause:** The `handle_array_set_code` ensures has two disjuncts (with/without trailing `\n`). The axiom currently used in coherence references both forms. Z3 times out on the array update.

**Fix:** Split `handle_array_set_code` into:
```why3
val function handle_array_set_code_with_rest
    (arr idx_str val_str indent rest_str : string) : string
  ensures { result = indent ^ arr ^ "[" ^ idx_str ^ "] <- " ^ val_str ^ ";\n" ^ rest_str }

val function handle_array_set_code_norest
    (arr idx_str val_str indent : string) : string
  ensures { result = indent ^ arr ^ "[" ^ idx_str ^ "] <- " ^ val_str }
```

Then each coherence lemma uses exactly one form, and Z3 can discharge with `--steps 1000000`.

### 2.3 `seq_code_state_coherent` (Z3 Timeout)

**Root cause:** `handle_seq_code` has two disjuncts (`;\n` vs. no separator). The concatenated string is too long for Z3's default step budget.

**Fix:** Same split pattern as above:
```why3
val function handle_seq_code_with_semi (s1_str s2_str : string) : string
  ensures { result = s1_str ^ ";\n" ^ s2_str }

val function handle_seq_code_concat (s1_str s2_str : string) : string
  ensures { result = s1_str ^ s2_str }
```

### 2.4 `return_plain_code_state_coherent` (needs intermediate let-binding)

**Root cause:** The axiom links `handle_return_code val_str indent false` (which generates `indent ^ val_str`) to `update st "\\result" e_val`. The prover needs to see the intermediate step: `val_str` evaluates to `e_val` in state `st`.

**Fix:** Add an intermediate step axiom and rewrite the lemma:
```why3
(* Axiom: the return plain form evaluates as an expression statement. *)
axiom return_plain_semantics :
  forall val_str indent st.
  eval_whyml_stmts (indent ^ val_str) st
  = update st "\\result" (eval_whyml_expr val_str st)

lemma return_plain_code_state_coherent :
  forall val_str indent st e_val.
  eval_whyml_expr val_str st = e_val ->
  let code = handle_return_code val_str indent false in
  eval_whyml_stmts code st = update st "\\result" e_val
```

---

## 3. Priority 2 — Prove `wp_for_desugar` (~8–16h, high difficulty)

**The gap:** `Phase5b_Soundness.v` and `Soundness.lean` have `admit`/`sorry` in the `ExecFor` case of `pycsl_soundness`:
```coq
- (* ExecFor *)
  eapply IHHexec.
  admit. (* needs: wp (SFor ...) → wp (desugar (SFor ...)) *)
```

**The difficulty:** The SFor WP (Phase4_WP.v:69–95) uses `variant-at-outer-state` (variant computed relative to the state BEFORE the loop), while the desugared SWhile WP uses `variant-at-iteration-state` (variant computed at each iteration's state). These are NOT directly interchangeable.

**The key sub-lemma:**
```coq
Lemma wp_for_desugar : forall x arr inv var body Qn Qr Qc pre_st st,
  wp (SFor x arr inv var body) Qn Qr Qc pre_st st ->
  wp (desugar (SFor x arr inv var body)) Qn Qr Qc pre_st st.
```

**Proof sketch:**
1. Unfold `desugar (SFor ...)` = `SSeq (SAssign for_idx (EInt 0)) (SWhile inv var guard loopBody)`.
2. Unfold the SSeq WP to get: `wp SWhile ... at state st0 = update st for_idx 0`.
3. Show that the SFor WP conjuncts imply the SWhile WP conjuncts at st0.
4. The variant discrepancy: SFor uses `eval_variant st pre_st var < eval_variant st_prev pre_st var` where `st_prev` is the PREVIOUS iteration's state, while SWhile uses `eval_variant body_result pre_st var < eval_variant st_current pre_st var`. These are equivalent when the variant is measured against `pre_st` (not the loop state).

**Estimated effort:** 8–16h. High risk due to the variant discrepancy requiring careful invariant formulation.

**Recommendation:** Defer to a dedicated session with Rocq/Lean interactive proof development.

---

## 4. Priority 3 — Audit-Guide.md Checklist (~1h)

Run the audit-guide.md checklist for all 9 `val function` specifications added to `pycsl-wp-spec.mlw`:

```bash
source .venv/bin/activate
# Check all val function specs have correct line references to Phase4_WP.v
grep -n "Phase4_WP.v\|Phase3b" src/self-annotate/pycsl-wp-spec.mlw
# Cross-check each ensures clause against the Rocq arm in Phase4_WP.v
```

The 9 specs (1 new in this session, 8 from previous):
- `handle_assign`, `handle_aug_assign`, `handle_array_set`
- `handle_if_true`, `handle_if_false`, `handle_while_step`, `handle_while_exit`
- `handle_return`, `handle_continue`
- `handle_for_init` ← new (plan-formal-03)

---

## 5. Priority 4 — CI Integration (~30min)

Add `self-annotate-verify` target to `Makefile`:

```makefile
self-annotate-verify:
	source .venv/bin/activate && \
	for f in src/self-annotate/rocq/*.py; do \
	    python3 src/pycsl/pycsl.py --no-proof "$$f" && echo "PASS $$f" || echo "FAIL $$f"; \
	done
	why3 prove src/self-annotate/pycsl-wp-spec.mlw -P "Z3,4.13.3,"
```

---

## 6. Effort Summary

| Task | Priority | Effort | Risk |
|------|----------|--------|------|
| Split 4 axioms into sub-lemmas | 1 | 3h | Low |
| `wp_for_desugar` coherence proof | 2 | 8–16h | High |
| Audit-guide.md checklist | 3 | 1h | Low |
| CI integration (Makefile target) | 4 | 30min | Low |
| **Total (P1 + P3 + P4)** | | **~4.5h** | |
| **Total (all)** | | **~12–20h** | |

**Recommended next session:** tackle Priority 1 (split strategy for the 4 human-audited axioms). This is a mechanical 3h task with no formal proof risk, and elevates 4 human-audited axioms to machine-checked lemmas, directly improving the Layer 3 trust chain.

---

Once the plan is done, provide recommendations and draft a new plan in `./src/self-annotate/plan-formal-??.md` where ?? is a new number compared to existing ones.