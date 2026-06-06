# plan-formal-02 — Extending the Layer 1/3 Bridge to All WP Arms

**Follows:** `plan-formal-01.md` (methodology + `src/` annotation complete)
**Companion:** `semantic-ceiling.md`, `pycsl-wp-spec.mlw`, `audit-guide.md`

---

## 1. What plan-formal-01 Achieved

| Item | Status |
|---|---|
| `src/self-annotate/src/*.py` annotated (277 `#@`) | Done — all 11 files pass `pycsl --no-proof` |
| `src/self-annotate/rocq/*.py` annotated (270 `#@`) | Done (pre-existing) |
| `src/self-annotate/lean/*.py` annotated (270 `#@`) | Done (pre-existing) |
| `pycsl-wp-spec.mlw` — `PyCSL_WP_Spec` module (10 WP `val`s) | Done |
| `pycsl-wp-spec.mlw` — `PyCSL_WP_Code` module (SAssign string spec) | Done |
| `pycsl-wp-spec.mlw` — `PyCSL_WP_Coherence` (SAssign coherence, Z3-proved) | Done |
| Ghost output tags for `_handle_assign_stmt` (SAssign) | Done in `rocq/` + `lean/` |

**One WP arm is fully bridged** (SAssign): Layer 1 ghost tags + Layer 3 string
spec + coherence lemma form a closed chain from proof to Python to WhyML string.
The remaining **nine arms** have Layer 1 structural contracts but no Layer 3
string spec and no ghost tags.

---

## 2. Recommendations

### Priority 1 — Ghost tags for the 9 remaining WP arms (Layer 1 strengthening)

**Why first:** Ghost tags are self-contained changes to the annotated Python files.
They require no proof assistant work and are verified by `pycsl --no-proof`. They
raise the Layer 1 contract from "output is non-empty" to "the correct dispatch
branch was taken." This is the cheapest improvement with the clearest formal value.

**Effort:** ~2h. Pattern is identical to the SAssign tags already in place.

### Priority 2 — `PyCSL_WP_Code` entries for the 8 non-SFor arms (Layer 3 string spec)

**Why second:** The SAssign pattern in `pycsl-wp-spec.mlw` generalises directly.
Each arm has a fixed string structure (e.g., SSkip → `"()"`, SReturn → `"raise Return_val"`).
Adding one `val function` per arm, with one or two `ensures` clauses capturing the
string structure, closes the Layer 3 string gap for all proven arms.

**Effort:** ~3h for 8 arms (avg 20min each). Z3 can discharge all coherence lemmas
given the SAssign precedent.

### Priority 3 — `desugar_correct` proof (close the SFor Layer B gap)

**Why third:** This is the deepest open gap (§8 of `self-annotate-global-plan.md`)
but also the most impactful: once proved, `_handle_for_stmt` gets a proper Layer B
contract and the SFor arm can be added to `pycsl-wp-spec.mlw`. Estimated 24–33h.

### Priority 4 — CI integration and coverage-report update

Add the new `src/` files to `make self-annotate` and update `coverage-report.md`.

---

## 3. This Plan: Ghost Tags + `PyCSL_WP_Code` for 9 Remaining Arms

### 3.1 Ghost Tag Pattern (recap from SAssign)

For each WP handler, add:
- `#@ ghost _<handler>_form = 0` at the top of the function body
- `#@ ghost _<handler>_form = N` inside each dispatch branch (N = 1, 2, …)
- `#@ ensures _<handler>_form == 1 or _<handler>_form == 2 or …` in the function contract

The ghost variable is erased at extraction. The `ensures` generates an SMT
proof obligation that one of the dispatch branches was taken — proving the
`if/elif/else` is exhaustive over the WP rule's cases.

### 3.2 Arm-by-Arm Ghost Tag Table

| WP Arm | Handler | Dispatch structure | Form values |
|---|---|---|---|
| `SSkip` | `"Pass"` branch in `_stmts_to_whyml` | single branch | 1 = pass emitted |
| `SAugAssign` | `_handle_aug_assign_stmt` | inline: int/array cases | 1 = int aug, 2 = array aug |
| `SArraySet` | `_handle_array_set_stmt` | inline: always one path | 1 = array-set emitted |
| `SSeq` | `_stmts_to_whyml` recursion | single recursive case | 1 = seq emitted |
| `SIf` | `_handle_if_stmt` | with/without else | 1 = if+else, 2 = if-only |
| `SWhile` | `_handle_while_stmt` | single path (complex body) | 1 = while emitted |
| `SFor` | `_handle_for_stmt` | single path | 1 = for desugared (**blocked**) |
| `SReturn` | `_handle_return_stmt` | with/without value | 1 = value return, 2 = bare return |
| `SContinue` | `_handle_continue_stmt` | single path | 1 = continue emitted |

**SFor:** Add ghost tag with form=1, but keep `#@ requires 1 == 1` — the tag
documents the dispatch path without claiming formal justification.

### 3.3 `PyCSL_WP_Code` String Specs (in `pycsl-wp-spec.mlw`)

Each `val function` below mirrors the string structure produced by the Python
handler. The `^` operator is already defined as `String.concat` in the module.

#### SSkip (Phase4_WP.v:21)
```why3
(* wp SSkip Q := Q st — the pass statement emits "()" *)
val function handle_skip_code (indent rest_str : string) : string
  ensures { result = concat indent (concat "()" (concat "\n" rest_str)) }
```

#### SAugAssign (Phase4_WP.v:26-30)
```why3
(* wp SAugAssign — two forms: int augmented assign or array element update *)
val function handle_aug_assign_code
    (lhs op_str rhs_str indent rest_str : string) (is_array : bool) : string
  ensures {
    not is_array ->
      result = indent ^ lhs ^ " := !" ^ lhs ^ " " ^ op_str ^ " " ^ rhs_str ^ ";\n" ^ rest_str
  }
  ensures {
    is_array ->
      result = indent ^ lhs ^ " <- " ^ rhs_str ^ ";\n" ^ rest_str
  }
```

#### SArraySet (Phase4_WP.v:32-35)
```why3
(* wp SArraySet — array element write: arr[i] <- v *)
val function handle_array_set_code
    (arr idx_str val_str indent rest_str : string) : string
  ensures {
    result = indent ^ arr ^ "[" ^ idx_str ^ "] <- " ^ val_str ^ ";\n" ^ rest_str
  }
```

#### SSeq (Phase4_WP.v:37-39)
```why3
(* wp SSeq — sequencing is string concatenation of s1 output and s2 output.
 * No separate val needed: _stmts_to_whyml implements SSeq by recursion.
 * Document the identity property: seq output = s1_str ++ s2_str *)
val function handle_seq_code (s1_str s2_str : string) : string
  ensures { result = concat s1_str s2_str }
```

#### SIf (Phase4_WP.v:41-43)
```why3
(* wp SIf — if/else dispatch; two forms: with else, without else *)
val function handle_if_code
    (cond_str then_str else_str indent : string) (has_else : bool) : string
  ensures {
    has_else ->
      result = indent ^ "if " ^ cond_str ^ " then\n" ^ then_str
             ^ indent ^ "else\n" ^ else_str
  }
  ensures {
    not has_else ->
      result = indent ^ "if " ^ cond_str ^ " then\n" ^ then_str
             ^ indent ^ "else ()\n"
  }
```

#### SWhile (Phase4_WP.v:45-66)
```why3
(* wp SWhile — while loop with invariant and variant annotations *)
val function handle_while_code
    (cond_str inv_str var_str body_str indent : string) : string
  ensures {
    result = indent ^ "while " ^ cond_str ^ " do\n"
           ^ indent ^ "  invariant { " ^ inv_str ^ " }\n"
           ^ indent ^ "  variant   { " ^ var_str ^ " }\n"
           ^ body_str
           ^ indent ^ "done\n"
  }
```

#### SReturn (Phase4_WP.v:96-97)
```why3
(* wp SReturn — raise Return exception with result value *)
val function handle_return_code
    (val_str indent : string) (has_value : bool) : string
  ensures {
    has_value ->
      result = indent ^ "raise (Return_val (" ^ val_str ^ "))\n"
  }
  ensures {
    not has_value ->
      result = indent ^ "raise Return_unit\n"
  }
```

#### SContinue (Phase4_WP.v:99-100)
```why3
(* wp SContinue — raise PyCSL_Continue exception *)
val function handle_continue_code (indent : string) : string
  ensures { result = indent ^ "raise PyCSL_Continue\n" }
```

### 3.4 Coherence Lemmas

For each arm above, add a coherence lemma in `PyCSL_WP_Coherence` following the
SAssign pattern. Each lemma has the form:

```why3
lemma handle_<arm>_code_state_coherent :
  forall <params> st.
  <eval hypotheses> ->
  let code = handle_<arm>_code <params> in
  eval_whyml_stmts code st = eval_whyml_stmts rest_str (<state_update> st)
```

The supporting semantic axioms (analogues to `assign_ref_update_semantics`) are:
- `skip_semantics`: `eval_whyml_stmts "()\n" st = st`
- `aug_assign_int_semantics`: `"lhs := !lhs op rhs;\n" updates lhs`
- `array_set_semantics`: `"arr[i] <- v;\n" updates arr at i`
- `seq_semantics`: `eval (concat s1 s2) st = eval s2 (eval s1 st)`
- `if_then_else_semantics`: branch dispatch based on cond
- `while_semantics`: fixpoint over inv/var/body triple
- `return_semantics`: `"raise (Return_val v)\n"` sets `"\result"`
- `continue_semantics`: `"raise PyCSL_Continue\n"` passes state through

All lemmas are expected to discharge under Z3 (matching the SAssign precedent).
Alt-Ergo may time out on string concatenation goals — use `Z3,4.13.3,` as the
prover.

---

## 4. Files to Modify

| File | Change |
|---|---|
| `src/self-annotate/rocq/Module6_WhyMLTranspiler.py` | Ghost tags on 9 remaining WP handlers |
| `src/self-annotate/lean/Module6_WhyMLTranspiler.py` | Same |
| `src/self-annotate/src/Module6_WhyMLTranspiler.py` | Same |
| `src/self-annotate/pycsl-wp-spec.mlw` | 8 new `val function` entries in `PyCSL_WP_Code`; 8 semantic axioms + 8 coherence lemmas in `PyCSL_WP_Coherence` |
| `src/self-annotate/coverage-report.md` | Update Layer B ghost tag count; add Layer 3 row for new arms |

---

## 5. Verification

```bash
# Layer 1: all three annotated trees pass
source .venv/bin/activate
for path in rocq lean src; do
    for f in src/self-annotate/${path}/Module6_WhyMLTranspiler.py; do
        python3 src/pycsl/pycsl.py --no-proof "$f" \
            && echo "PASS [$path]" || echo "FAIL [$path]"
    done
done

# Layer 3: all new string-spec goals discharge
why3 prove src/self-annotate/pycsl-wp-spec.mlw -P "Z3,4.13.3,"
```

---

## 6. Effort and Risk

| Task | Effort | Risk |
|---|---|---|
| Ghost tags for 9 arms (rocq/ + lean/ + src/) | 1.5h | Low — pattern established |
| `PyCSL_WP_Code` 8 `val function` entries | 1.5h | Low — string structures are simple |
| `PyCSL_WP_Coherence` axioms + lemmas for 8 arms | 2h | Medium — string concat goals |
| Coverage-report update | 30min | Low |
| **Total** | **~5.5h** | |

**SFor remains blocked** on `desugar_correct` (§8 of global plan, est. 24–33h).
All other arms can be completed independently.


---

Once the plan is done, provide recommendations and draft a new plan in `./src/self-annotate/plan-formal-??.md` where ?? is a new number compared to existing ones.