# Phase 3.0 — census refinement: clean collection-fold subset per family

**2026-07-08. Measurement/classification ONLY — no `src/pycsl` / mirror edits, ledger untouched,
count 1247 unchanged.** Executes `phase3.md` §2 (the go/no-go). Reads the LIVE `src/pycsl` bodies of the
`\trusted` collection-result builders (the ~259 pool from `wall-plan-v3-phase0.md` §1, buckets "builds/
mutates a collection" (236) + "structural literal-key recursion building a collection" (23)) and classifies
each **by its live body**, not its outer walk shape.

Reproducibility: `scratchpad/phase3_census.py` (AST pre-filter) + `scratchpad/phase3_census_rows.json`
(per-method file/name/family/mode/clean/reason). Every CLEAN row was hand-verified against its live body;
the pre-filter's own false-positives were caught and fixed during verification (see §5).

---

## 0. Bottom line — GATE VERDICT

| family | pool (result-typed builders) | **CLEAN (live-verified)** | complicated | verdict |
|---|--:|--:|--:|---|
| **A-set** | 50 | **9** | 41 | **GO (≥5) → Phase 3.1** |
| **A-dict** | 40 | **1** | 39 | NO-GO (<5) → bank |
| **A-list** | 74 | **0** | 74 | NO-GO → bank |
| A-bool (predicate) | 23 | n/a (not a build target) | — | out of scope for 3.1/3.2/3.3 |

**GO: A-set only.** Its clean subset (9 methods) clears the ≥5 threshold — and these are exactly the T-A
generic-walk catamorphisms whose by-ref twin (`find_named_expr_targets`) already converted certified in
Phase 0. **A-dict (1) and A-list (0) are NO-GO and bank** — dominated by sibling-helper composition, in-place
subject rewrite, and comprehension returns, i.e. the same composed/dependent character that deferred Phases
1b and 2. The census over-count warning held for A-list/A-dict; A-set is the one honest, bounded prize.

**Proceed:** Phase **3.1 (A-set)** GO. Phases **3.2 (A-dict)** and **3.3 (A-list)** bank as
`TRUSTED(essential)`; the single clean A-dict fold (`_subst_type_in_ir`) is not worth a per-family value-model
build on its own (may ride the A-set template later if the set→map algebra generalizes; not gated now).

---

## 1. Pool derivation and totals

`\trusted` methods in the 9 IR-consuming modules with a live body: **577** (+31 renamed/absent = NO-LIVE-BODY).
Of these the **result-typed collection builders** (a returned local `set/list/dict`, a by-ref mutated param
collection, or a returned comprehension) number **164**:

| result family | total | modes (return-local / by-ref-param / comprehension) |
|---|--:|---|
| A-set | 50 | 43 / 5 / 2 |
| A-list | 74 | 49 / 21 / 4 |
| A-dict | 40 | 33 / 5 / 2 |

Plus **23** A-bool recursive predicates (`any`/`all` / bool-returning self-recursion — v3's 16-bucket, here 23),
and 390 "other" (string/f-string builders, non-builder collection-touchers, flat scalar readers). The 164
typed builders + the string-builder slice of "other" + the 23 predicates ≈ the v3 ~259 "collection-result"
count; §0's gate is on the 164 result-typed builders, the actual fold targets.

## 2. CLEAN criteria (all must hold; else COMPLICATED + deciding feature)
Single self-recursive walk; accumulate into the returned/by-ref collection via `|=`/`+=`/`.update`/`.add`/
`.append`/`out[k]=`; **literal** key reads of the subject only (no `d.get(var)` / `d[var]`); NO sibling-helper
call; NO composed second fold; NO short-circuit / early-return-in-loop / **value-dependent recursion guard**
(e.g. binder-subtraction on a specific child); NO subject mutation (accumulator ≠ walked subject).

---

## 3. CLEAN subsets (file::name — hand-verified)

### A-set — 9 CLEAN
Two clean sub-shapes:

**Sub-shape A — generic `.values()`/`.items()` catamorphism** (`if isinstance(dict): [literal-key pre-action
→ acc]; for v in obj.values(): acc |= self(v)/acc.add(...); elif isinstance(list): for x: self(x)`):
1. `core_ir_semantic.py::_collect_call_targets` (14L) — `acc.add(node["func"])` + `.rsplit`; uniform values-fold.
2. `core_ir_semantic.py::_hp_collect_written` (12L) — `written.add(arr.get("field"))` under literal `stmt=="ArraySet"` guard; uniform values-fold (by-ref).
3. `frontend/ir_resolve.py::_collect_calls` (12L) — `calls |= _collect_calls(v)`; literal `type=="Call"`.
4. `module6_whyml/functions.py::_collect_assign_targets` (10L) — `acc.add(node["target"])` under literal `stmt in (Assign,AugAssign)`; by-ref.
5. `module6_whyml/ir_scanner.py::collection_binder_kinds` (18L) — `found |= self(v)`; literal `type in (Forall,Exists)` + `binder_type`.
6. `module6_whyml/scc.py::find_calls_in_ir` (12L) — `calls |= self(v)`; literal `type=="Call"`, `func in set`.
7. `module6_whyml/scc.py::find_self_method_calls` (27L) — `out |= self(v)`; literal `func`/`type`, entry precond guard only (not in-loop).

**Sub-shape B — fixed-child structural recursion** (recurse into named child keys, uniform accumulate):
8. `module6_whyml/ir_scanner.py::find_ghost_vars` (13L) — `ghosts.update(self(stmt["body"]/["orelse"]))`; literal `stmt` tag dispatch, uniform `.add`/`.update`.
9. `frontend/Module5_IREmitter.py::_scan_2d_in_expr` (25L) — `result.add(root["name"])` on `a[i][j]` pattern; type-dispatched recursion into `value`/`index`/`left`/`right`/`args`, all literal keys, uniform.

### A-dict — 1 CLEAN
1. `frontend/monomorphize.py::_subst_type_in_ir` (23L) — functional rebuild: `new={}; for k,v in node.items(): new[k]=(concrete if literal-guard else self(v)); return new`. Literal-key guards (`type=="Var"`, `k=="name"`, `k=="return_annotation"`); builds a NEW dict (does not mutate `node`); uniform.

### A-list — 0 CLEAN
No A-list builder is a clean self-contained fold. All 74 fail on sibling-helper composition (64), non-self /
flat accumulation (67), variable-key subject reads (14), comprehension-not-fold (4), or subject mutation (6).

---

## 4. Spot-check examples

### CLEAN (with live snippet)

**`find_calls_in_ir` (A-set, sub-shape A)** — the canonical clean catamorphism:
```python
def find_calls_in_ir(obj, func_names_set):
    calls = set()
    if isinstance(obj, dict):
        if obj.get("type") == "Call" and obj.get("func") in func_names_set:
            calls.add(obj["func"])                 # literal-key pre-action → acc
        for v in obj.values():
            calls |= find_calls_in_ir(v, func_names_set)   # uniform values-fold
    elif isinstance(obj, list):
        for item in obj:
            calls |= find_calls_in_ir(item, func_names_set)
    return calls
```
Qualifies: single self-recursive walk; `calls |= self(v)` fold; literal keys only; no sibling call; no
short-circuit; no subject mutation.

**`_hp_collect_written` (A-set, by-ref)** — literal-key pre-action, by-ref accumulator:
```python
def _hp_collect_written(node, written):
    if isinstance(node, dict):
        if node.get("stmt") == "ArraySet":
            arr = node.get("array")
            if isinstance(arr, dict) and arr.get("type")=="FieldGet" and arr.get("object")=="self":
                written.add(arr.get("field"))      # all literal-key reads
        for v in node.values():
            _hp_collect_written(v, written)
    elif isinstance(node, list):
        for x in node:
            _hp_collect_written(x, written)
```

**`_subst_type_in_ir` (A-dict)** — functional dict rebuild, does NOT mutate the subject:
```python
def _subst_type_in_ir(node, tvar, concrete):
    if isinstance(node, dict):
        new = {}
        for k, v in node.items():
            if k=="name" and v==tvar and node.get("type")=="Var":  new[k]=concrete
            elif k=="return_annotation" and v==tvar:               new[k]=concrete
            else:                                                   new[k]=_subst_type_in_ir(v,tvar,concrete)
        if "type" in new and new["type"]==tvar: new["type"]=concrete
        return new
    if isinstance(node, list): return [_subst_type_in_ir(x,tvar,concrete) for x in node]
    return node
```

### COMPLICATED (with deciding feature)

- **`find_assigned_vars` (A-set)** — *composed second fold*: calls the sibling walk
  `find_named_expr_targets(...)` inside its own recursion; not self-contained.
- **`_ir_free_vars` (A-set)** — *value-dependent recursion guard* (demoted from the script's CLEAN):
  the `Forall`/`Exists`/`ForallItems` arms do `_ir_free_vars(node["body"]) - {node["var"]}` — recurse on a
  *specific* child and **set-subtract** the binder. Non-uniform / non-monotone; not a single uniform fold.
  (The script missed this because the returns are top-level type dispatch, not in-loop — exactly the
  over-count trap; caught by eye.)
- **`_rewrite_ir_calls` (A-dict)** — *subject mutation (acc==subject)*: `obj["func"]=new_name` rewrites the
  walked tree **in place** (accumulator IS the subject). An in-place transform, not a result-building fold.
- **`_substitute` (A-dict)** — *sibling-helper call* (`deepcopy`, `partition`) + variable-key subject read.
- **`inline_stmts` (A-list)** — *sibling-helper composition* (`_expand`, `_global_call_target`,
  `_hoist_calls_in_expr`) + `d.get(var)` + subject mutation. Heavily composed.

---

## 5. Honesty notes (script false-positives caught during hand-verification)

The AST pre-filter over-counted AND under-counted before correction — proving the task's premise that the
script alone cannot decide:
1. **Under-count fixed:** typing-generic annotations (`calls: Set[str] = set()`) were misread as
   variable-key subject reads (`Set[str]` = `Subscript(Name('Set'), Name('str'))`), wrongly disqualifying 7+
   genuine T-A folds. Excluded `TYPING_NAMES`.
2. **Under-count fixed:** `str` methods (`.rsplit`, `.startswith`, …) were counted as sibling-helper calls;
   added to the benign allowlist. Surfaced `_collect_call_targets`, `_ir_free_vars` (later re-demoted on
   merit), `find_self_method_calls`.
3. **Over-count fixed:** `_rewrite_ir_calls` was script-CLEAN but mutates the subject in place — added the
   `accumulator == walked-subject` disqualifier.
4. **Over-count caught by eye (not scriptable):** `_ir_free_vars` passed every script check yet is complicated
   (binder-subtraction). Demoted manually.

Two **borderline** methods kept COMPLICATED conservatively (variable key ranging over a literal tuple —
`stmt[key] for key in ("body","orelse")`): `find_record_vars`, `find_record_var_classes`. Semantically clean
structural folds; flagged because the AST key is a variable. Reclassifying them CLEAN would raise A-set to 10
and A-dict to 2 — does not change any gate verdict.

---

## 6. Verdict summary
- **A-set: 9 clean ≥ 5 → GO.** Phase 3.1 proceeds: build the returned-`set string` / by-ref-set fold algebra
  + axiom-free Rocq/Lean certificate, convert the 9 (7 uniform-values catamorphisms + 2 fixed-child structural
  recursions; note the template must emit BOTH sub-shapes A and B).
- **A-dict: 1 clean < 5 → NO-GO, bank.** Single fold (`_subst_type_in_ir`); not worth a standalone `pydict`
  result-model build. Revisit only if the A-set algebra generalizes to `map` for free.
- **A-list: 0 clean → NO-GO, bank.** No self-contained list fold exists in the residual.
- **A-bool** (23 recursive predicates) is not a collection-result build target; out of scope for 3.1/3.2/3.3.

The prize is A-set's certified returned-collection fold coupled to `pyval` — measured, bounded, honest.
