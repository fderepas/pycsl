# Ghost Variable Types — Post-Implementation Recommendations (Phase 3)

## Completed Work (Sessions 5–6)

All items from `plan-ghost-recommendation-02.md` are now implemented:

| Item | Description | Status |
|------|-------------|--------|
| E1 | End-to-end proof tests for ghost tuple and ghost list | ✅ (0305, 0306) |
| E2 | Ghost set `\set_union` with `\set_mem` in no-proof context | ✅ (0308) |
| E3 | `\proj` arity mismatch XFAIL tests | ✅ (0302, 0303) |
| E4 | Ghost string `+=` rejected at Module4 + XFAIL test | ✅ (0304) |
| E5 | Ghost set `+=` shorthand | ✅ (0301, completed in session 4) |
| E6 | `\map_eq` in loop invariants test | ✅ (0307) |
| E7 | Transpiler limits documentation — ghost type → Why3 `use` table | ✅ |

New reference tests added:

| Test | Feature |
|------|---------|
| 0302 | XFAIL: `\proj(t, n)` dynamic index rejected at Module4 |
| 0303 | XFAIL: `\proj(p, 2)` on `tuple2` arity mismatch (Why3 type error) |
| 0304 | XFAIL: `#@ ghost s += "x"` ghost string augmented assignment rejected at Module4 |
| 0305 | Ghost tuple2 proof: `\fst`/`\snd` in loop invariants, proven by Alt-Ergo |
| 0306 | Ghost list length proof: `\list_length(l) == i` loop invariant, proven by Alt-Ergo |
| 0307 | Ghost dict `\map_eq` in loop invariant (--no-proof) |
| 0308 | Ghost set `\set_union` with `\set_mem` (--no-proof) |

Test suite final: **300/302 passed** (2 pre-existing failures: 0290, 0291).

### Bug fixes in this session

Two bugs were discovered and fixed during E1 implementation:

1. **Ghost aug-assign type override bug (Module6)**: Augmented-assign ghost statements
   (`+=`, `-=`, `*=`) carry `ghost_type == "int"` (default) because the grammar transformer
   `ghost_aug_assign` does not propagate `declared_type`. Module6's `_handle_ghost_assign_stmt`
   now falls back to the tracked sets (`_ghost_list_vars`, `_ghost_set_vars`, `_ghost_dict_vars`,
   `_ghost_tuple_vars`, `_ghost_string_vars`) to resolve the true type for aug-assigns.
   **Impact**: `ghost l += x` was emitting `ghost l := !l + !x` (wrong) instead of
   `ghost l := Cons !x !l`.

2. **Ghost type scope overwrite bug (Module4)**: Augmented-assign ghost declarations
   (`op != "="`) were overwriting the registered type in `current_scope` with `"int"` (the
   default `declared_type`), making the E4 validation `current_scope.get(target) == "string"`
   always false. Fixed by only using `declared_type` from declarations (`op == "="`) and
   never overwriting an already-registered type from an aug-assign.

3. **Why3 list function names (Module6)**: `List.length`, `List.nth`, `List.mem`, `List.(++)`
   are not valid in Why3 — the correct unqualified names are `length`, `nth`, `mem`, `(++)`,
   exported from `list.Length`, `list.Nth`, `list.Mem`, `list.Append` respectively. Fixed in
   all handler methods (`_handle_list_length_expr`, `_handle_nth_expr`, `_handle_mem_expr`,
   `_handle_append_expr`) in the live, rocq, and lean copies of Module6.

### Self-annotated copies updated

- Module4 rocq + lean: ghost aug-assign type preservation fix; ghost string `+=` validation
- Module6 rocq + lean: ghost aug-assign type override fix; list function name corrections

---

## Remaining Deferred Work (Phase 4)

### F1. End-to-end proof tests for ghost dict

Ghost dict proofs with `Map.get`/`Map.set` axioms are tractable when restricted to shallow
key lookups. A minimal provable test:

```python
#@ ghost d : ghost_dict = \empty_map
#@ loop invariant \map_get(d, i) == i or i == 0
```

However, proving `Map.get (Map.set d k v) k = v` requires the `map.MapExt` or
`map.Map` axiom `Map.get_set`. Z3 handles this well; Alt-Ergo may need hints. Create a
test with a simple invariant that only references the most recently written key.

### F2. End-to-end proof test for ghost tuple3/tuple4

Test 0305 covers `tuple2`. A similar test for `tuple3` with `\proj` on indices 0/1/2 would
extend proof coverage. These are native Why3 tuples and should prove easily.

### F3. Proof test for `\set_mem` after `\set_union`

Test 0308 is `--no-proof`. A restricted bounded-range version of `\set_mem(k, \set_union(s1, s2))`
where `k`, `s1`, `s2` are bounded by a concrete constant (e.g., `0 <= k and k < 10`) would
help validate the functional-lambda set representation.

**Documented restriction (already in transpiler-limits.md §10):** Restrict `\set_union` /
`\set_inter` / `\set_diff` operands to bounded integer ranges for best SMT performance.

### F4. `\map_eq` full proof test

Test 0307 is `--no-proof`. A proof test where `\map_eq(d1, d2)` is preserved through
`\map_set` operations on both dicts in lockstep would validate that `forall k, Map.get d1 k = Map.get d2 k`
is dischargeable by Z3. Expected to work since `Map.set` is axiomatic in Why3.

### F5. Ghost list `\nth`/`\mem` proof test

`\nth` (emitting `nth i !l`) and `\mem` (emitting `mem x !l`) are implemented but untested
with proof. A simple test tracking a `ghost_list` log and proving `mem v !log` after
inserting `v` via `Cons` would validate these operations.

### F6. Ghost array proof test

Ghost array in the hoare model uses `Array.make`/`Array.copy`. A proof test tracking a
snapshot array and showing that `snap[i] = arr[i]` holds after copying would validate the
`ghost_array_set` infrastructure.

### F7. Run self-annotation pipeline on Module6

Now that all ghost infrastructure is complete and all self-annotated copies are synced,
re-running the self-annotation pipeline on `Module6_WhyMLTranspiler.py` would strengthen
the `#@ requires 1 == 1` placeholder contracts currently on all ghost handler methods.
The pipeline can now reason about the IR dict structure and produce meaningful preconditions
like `#@ requires "type" in expr and "list" in expr`.

### F8. RAG index rebuild

Run `./bin/update-rag.sh` after any further skill updates to keep the agent RAG index current.

---

## Recommendations for Phase 4

1. **F1 (ghost dict proof)** is the highest priority — it's the only ghost type without
   a full proof test. Use Z3 explicitly (`-p Z3`) since it has better map axiom support.

2. **F3 (set_union bounded proof)** validates the most complex ghost operation. If Z3
   can discharge it for bounded ranges, document the range requirement clearly.

3. **F2/F5/F6** are low-effort extensions that complete the proof coverage matrix.

4. **F7 (self-annotation pipeline)** can run opportunistically without blocking the
   other items.

5. **F4 (\map_eq proof)** is expected to be trivial with Z3; do it alongside F1.

---

Once the plan is done, provide recommendations and draft a new plan in
`./src/self-annotate/plan-ghost-recommendation-??.md` where ?? is a new number.

--- new version::

---

Do not modigy this file.

Once the plan is done, provide recommendations, future paths, especially around the reduction of the Trusted Computing Base in `./src/self-annotate/plan-ghost-recommendation-??.md` where ?? is a new number.
