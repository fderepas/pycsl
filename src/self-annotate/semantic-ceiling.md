# Solving the Semantic Ceiling: From String Non-Emptiness to WP Substitution Equivalence

**Status:** Active plan
**Companion documents:** `self-annotate-global-plan.md`, `pycsl-wp-spec.mlw`, `audit-guide.md`

---

## 1. The Exact Gap

`_handle_assign_stmt` in `Module6_WhyMLTranspiler.py` generates a WhyML string.
The best Layer 1 PyCSL contract expressible today is:

```python
#@ requires stmt != 0
#@ ensures \result != ""
```

The formal correspondent in `pycsl-wp-spec.mlw` says:

```why3
val handle_assign (x: ident) (e_val: value) (st: state) : state
  ensures { result = update st x e_val }
```

These two specs are **not connected**. Layer 3 (`pycsl-wp-spec.mlw`) captures
state-transformation semantics; the Python function produces a string. No proof
links "the output string, when evaluated by Why3, performs the right state update."

The missing connection:

```
_handle_assign_stmt output (str)
        │
        │  eval_whyml_stmts  (abstract, unformalized)
        ▼
state transformation: st' = update st x (eval_expr st e)
        ↑
        │  current Layer 3 handle_assign val spec
        │
pycsl-wp-spec.mlw
```

Neither Layer 1 nor the current Layer 3 spec crosses this bridge.

---

## 2. Why String Predicates Alone Are Insufficient

Even a hypothetical `\contains(\result, "let ")` predicate would be syntactically
necessary but not semantically sufficient:

- `let x = ref 42 in` is correct for `SAssign x (EInt 42)` when `42 = eval_expr σ e`.
- `let x = ref 0 in` passes the same predicate but is wrong if `eval_expr σ e ≠ 0`.

Full equivalence requires: ∀ Q, the output string evaluated by Why3 satisfies Q iff
`Q[x ↦ eval_expr σ e]`. This requires a formal model of WhyML evaluation inside the
contract layer — which is precisely what PyCSL's contract language cannot currently
express.

---

## 3. Solution: Two Complementary Layers

### Step 1 — Ghost Output Tags (Layer 1, tractable now)

Add PyCSL ghost variables to track which binding form was emitted. Ghost variables
are erased at extraction but generate SMT proof obligations via the `ensures` clause.

**Pattern for `_handle_assign_stmt`:**

```python
#@ ghost _assign_form = 0
def _handle_assign_stmt(self, stmt, rest, local_refs, declared_refs, indent, in_loop):
    target = stmt["target"]
    ...
    if target not in declared_refs:
        declared_refs.add(target)
        ...
        #@ ghost _assign_form = 1   # let-binding (first occurrence)
        code = f"let {safe_target} = ..."
    else:
        ...
        #@ ghost _assign_form = 2   # ref-update (subsequent occurrence)
        code = f"{safe_target} := ..."
    ...
#@ ensures _assign_form == 1 or _assign_form == 2
```

**What this proves:** the function always takes one of the two WP-derived branches;
neither branch is dead code; the if/else dispatch is exhaustive.

**What it does NOT prove:** that the specific value `e_val` equals `eval_expr σ e`.

**Effort:** low — uses current PyCSL ghost variable syntax, no grammar changes.

The same pattern applies to all 10 WP handlers. The ghost tag values for each:

| Handler | Tag 1 | Tag 2 | Tag 3 |
|---------|-------|-------|-------|
| `_handle_assign_stmt` | let-binding | ref-update | shared-var-assign |
| `_handle_while_stmt` | while-body | while-exit | — |
| `_handle_for_stmt` | for-body | for-exit | — |
| Inline SReturn | return-with-value | — | — |
| Inline SContinue | continue-emitted | — | — |
| Inline SSkip/Pass | pass-emitted | — | — |

---

### Step 2 — String-Level `val` Specs in `pycsl-wp-spec.mlw` (Layer 3)

Add a second module `PyCSL_WP_Code` to `pycsl-wp-spec.mlw` that specifies the
output STRING rather than the state transformation. This uses Why3's built-in
`string.String` theory (`^` for concatenation).

```why3
module PyCSL_WP_Code

  use string.String
  use bool.Bool

  (* String-level spec for SAssign code generation.
   *
   * Parameters:
   *   lhs:      WhyML identifier for the assignment target
   *   rhs_str:  WhyML expression string for the RHS value
   *   declared: whether lhs is already in the ref-declared set
   *   indent:   indentation prefix string
   *   rest_str: pre-rendered string for the continuation
   *
   * Formal correspondent: Phase4_WP.v:23-24
   *   wp (SAssign x e) Q := [x ↦ eval_expr σ e] Q
   *
   * Two branches:
   *   declared=false → WhyML `let lhs = ref rhs_str in\n` + rest
   *   declared=true  → WhyML `lhs := rhs_str;\n` + rest
   *
   * The array/lambda/dict variants produce `let lhs = rhs_str in\n`
   * (no `ref`) — captured by the disjunction in the second ensures.
   *)
  val handle_assign_code
      (lhs rhs_str indent rest_str : string) (declared : bool) : string
    ensures {
      declared ->
        result = indent ^ lhs ^ " := " ^ rhs_str ^ ";\n" ^ rest_str
    }
    ensures {
      not declared ->
           result = indent ^ "let " ^ lhs ^ " = ref " ^ rhs_str ^ " in\n" ^ rest_str
        \/ result = indent ^ "let " ^ lhs ^ " = "     ^ rhs_str ^ " in\n" ^ rest_str
    }

end
```

**What this proves:** the output string has exactly the expected syntactic structure
for each of the two WP-derived binding forms.

**What it does NOT prove yet:** that `rhs_str` is `expr_to_whyml(e)` for the
correct expression `e` — this requires the coherence lemma (Step 3).

---

### Step 3 — Coherence Lemma: Connecting String-Level to State-Level

Add a third module `PyCSL_WP_Coherence` to `pycsl-wp-spec.mlw` that states the
bridge theorem between string generation (Layer 3 code spec) and state semantics
(Layer 3 state spec).

```why3
module PyCSL_WP_Coherence

  use PyCSL_WP_Spec
  use PyCSL_WP_Code
  use string.String

  (* Abstract evaluation of a WhyML expression string in a given state.
   * Axiomatized — the full WhyML interpreter is not in scope.
   * Human-audited: the axioms below are checked against Phase2_State.v. *)
  val function eval_whyml_expr (s: string) (st: state) : value

  (* Abstract evaluation of a WhyML statement string in a given state. *)
  val function eval_whyml_stmts (s: string) (st: state) : state

  (* Axiom SAssign-RefUpdate: a ref-update statement transforms state correctly.
   * `lhs := rhs_str;\n` followed by `rest_str` in state `st` produces the same
   * final state as updating lhs with eval_whyml_expr(rhs_str, st), then
   * running rest_str.
   * This axiom is the semantic content of the WP SAssign arm. *)
  axiom assign_ref_update_semantics :
    forall lhs rhs_str rest_str indent st.
    eval_whyml_stmts
      (indent ^ lhs ^ " := " ^ rhs_str ^ ";\n" ^ rest_str) st
    =
    eval_whyml_stmts rest_str (update st lhs (eval_whyml_expr rhs_str st))

  (* Axiom SAssign-LetRef: a let-ref-binding has the same state semantics. *)
  axiom assign_let_ref_semantics :
    forall lhs rhs_str rest_str indent st.
    eval_whyml_stmts
      (indent ^ "let " ^ lhs ^ " = ref " ^ rhs_str ^ " in\n" ^ rest_str) st
    =
    eval_whyml_stmts rest_str (update st lhs (eval_whyml_expr rhs_str st))

  (* Axiom SAssign-Let (array/lambda/dict form, no ref): same semantics. *)
  axiom assign_let_semantics :
    forall lhs rhs_str rest_str indent st.
    eval_whyml_stmts
      (indent ^ "let " ^ lhs ^ " = " ^ rhs_str ^ " in\n" ^ rest_str) st
    =
    eval_whyml_stmts rest_str (update st lhs (eval_whyml_expr rhs_str st))

  (* Coherence theorem: the string emitted by handle_assign_code, when evaluated,
   * produces the state transformation specified by handle_assign.
   *
   * Proof sketch:
   *   Case declared=true:  by handle_assign_code ensures + assign_ref_update_semantics
   *   Case declared=false: by handle_assign_code ensures + assign_let_ref_semantics
   *                        or assign_let_semantics (disjunction in ensures)
   *)
  lemma assign_code_state_coherent :
    forall lhs e_val_str rest_str indent declared st e_val.
    eval_whyml_expr e_val_str st = e_val ->
    let code = handle_assign_code lhs e_val_str indent rest_str declared in
    eval_whyml_stmts code st
    =
    eval_whyml_stmts rest_str (update st lhs e_val)

end
```

**What this proves:** IF `_handle_assign_stmt` produces output whose structure
matches `handle_assign_code lhs e_val_str indent rest_str declared` (established
by the ghost tag + Layer 3 code spec), AND IF `e_val_str` is the WhyML rendering
of `eval_expr σ e` (established by `_expr_to_whyml` contracts + human audit),
THEN the output transforms state as the WP rule requires.

---

## 4. Why3 String Theory Compatibility

Why3 provides `use string.String` with `(^)` for concatenation.
The SMT backends (Z3 ≥ 4.8, Alt-Ergo ≥ 2.4) handle string theories.

The axioms above have universally quantified string variables. Z3's seq/string
theory handles these when the structure is regular (fixed literal separators
between variables). Risk: **low** for the axioms (direct structural patterns);
**medium** for the coherence lemma (requires combining two ensures clauses with
the axioms — may need `--steps 100000` or a manual Rocq proof).

Fallback if VCs don't discharge: convert `assign_code_state_coherent` from
`lemma` to `axiom` and document it as human-audited in `audit-guide.md`,
following the same pattern as the existing Layer 3 axioms.

---

## 5. What Remains After This Plan

This plan closes the gap for `_handle_assign_stmt`. The remaining gap:

**Not proved here:** that `_handle_assign_stmt` ACTUALLY calls `handle_assign_code`
with the correct `lhs` and `e_val_str`. This connection requires either:

1. A Rocq/Lean proof that the Python implementation is a refinement of the spec
   (equivalent to CompCert-style extraction — out of scope for PyCSL).
2. The human-audit approach in `audit-guide.md` (current best practice).

The full formal bridge with no human audit requires extracting Python from Rocq,
which is architecturally out of scope. The layered trust model (L0 → L1 → L2 → L3
+ human audit) is the intended answer, with this plan closing the L3 string gap.

---

## 6. Scope and Effort

| Step | Change | Effort | Risk |
|------|--------|--------|------|
| Ghost output tags — `_handle_assign_stmt` | Layer 1, `rocq/` and `lean/` | 30min | Low |
| Ghost output tags — all 9 remaining WP handlers | Layer 1, `rocq/` and `lean/` | 1–2h | Low |
| `PyCSL_WP_Code` module (SAssign) | `pycsl-wp-spec.mlw` | 1h | Low |
| `PyCSL_WP_Coherence` axioms + lemma (SAssign) | `pycsl-wp-spec.mlw` | 2–3h | Medium |
| Extend to remaining 8 WP arms (not SFor) | `pycsl-wp-spec.mlw` | +4–6h | Medium |
| SFor string-level spec | Blocked on `desugar_correct` | Blocked | — |

**Total for SAssign end-to-end (Steps 1–4):** ~4–5h.

---

## 7. Files Modified

| File | Change |
|------|--------|
| `src/self-annotate/pycsl-wp-spec.mlw` | Add `PyCSL_WP_Code` and `PyCSL_WP_Coherence` modules |
| `src/self-annotate/rocq/Module6_WhyMLTranspiler.py` | Add ghost output tags to all 10 WP handlers |
| `src/self-annotate/lean/Module6_WhyMLTranspiler.py` | Same |
| `src/self-annotate/coverage-report.md` | Update annotation count and add Layer 3 row |

---

## 8. Verification Commands

```bash
# Layer 3: check Why3 accepts the extended spec
# Note: assign_code_state_coherent requires Z3 (string theory); Alt-Ergo times out.
why3 prove src/self-annotate/pycsl-wp-spec.mlw -P "Z3,4.13.3,"

# Layer 1: check ghost-tagged Python still passes pycsl --no-proof
source .venv/bin/activate
python src/pycsl/pycsl.py --no-proof src/self-annotate/rocq/Module6_WhyMLTranspiler.py
python src/pycsl/pycsl.py --no-proof src/self-annotate/lean/Module6_WhyMLTranspiler.py
```
