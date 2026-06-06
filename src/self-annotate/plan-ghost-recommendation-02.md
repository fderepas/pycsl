# Ghost Variable Types — Post-Implementation Recommendations (Phase 2)

## Completed Work (Sessions 3–4)

All items from `plan-ghost-recommendation-01.md` are now implemented:

| Item | Description | Status |
|------|-------------|--------|
| D1 | Module6 self-annotated copy full sync (rocq + lean) | ✅ |
| D2 | Ghost string `\str_length` and `\str_sub` builtins | ✅ |
| D3 | Secondary Module6 touch-point audit for ghost strings | ✅ (no changes needed) |
| D4 | Ghost dict `+=` shorthand (`ghost d += \mktuple(k, v)`) | ✅ |
| D5 | Ghost set union/inter/diff reference test | ✅ (test 0299) |
| D6 | Ghost list `+=` shorthand (`ghost l += x`) | ✅ |
| D7 | `\proj` boundary verification (idx=1 for tuple2) | ✅ |
| D8 | RAG index rebuild | ✅ |

New reference tests added:

| Test | Feature |
|------|---------|
| 0298 | Ghost string `\str_length`, `\str_sub` |
| 0299 | Ghost set `\set_union`, `\set_inter`, `\set_diff` (--no-proof) |
| 0300 | Ghost list `+=` shorthand + ghost dict `+=` shorthand |

Test suite final: **292/294 passed** (2 pre-existing failures: 0290, 0291).

Self-annotated copies updated:
- Module2 rocq + lean: `StrLengthExpr`, `StrSubExpr` dataclasses + grammar + transformers
- Module4 rocq + lean: `_CSL_CHILDREN_MAP` entries for `StrLengthExpr`, `StrSubExpr`
- Module5 rocq + lean: `_CSL_HANDLERS` + handler methods for `StrLengthExpr`, `StrSubExpr`
- Module6 rocq + lean: Full ghost infrastructure sync (see D1 details below)

### D1 Module6 sync summary

Added to both rocq and lean `Module6_WhyMLTranspiler.py` self-annotated copies:
- `IRScanner.uses_ghost_type` static method
- Ghost entries in `_EXPR_DISPATCH` (30 new entries)
- `_e()` helper method
- 30 ghost expression handler methods (`_handle_mktuple_expr` … `_handle_append_expr`)
- `_handle_str_length_expr`, `_handle_str_sub_expr`
- `_handle_ghost_assign_stmt` — full typed dispatch (string/tuple/array/dict/list/set/int)
- `_handle_ghost_array_set_stmt`
- `_expr_to_whyml_string_ctx`
- `_ghost_string_vars`, `_ghost_array_vars`, `_ghost_dict_vars`, `_ghost_list_vars`,
  `_ghost_set_vars`, `_ghost_tuple_vars: Dict[str, int]` in `_reset_function_state`
- `needs_map_ghost`, `needs_list_ghost` in `_scan_preamble_needs` return dict
- Ghost library `use` declarations in `_emit_preamble_uses`

### D3 audit result

No code changes were required:
- `_coerce_str_arg` only hashes quoted string literals (`"..."`), not ghost vars (`!acc`) — correct
- `_handle_fstring_expr` operates on Python body expressions, not `#@` annotations — ghost string vars cannot appear in f-string lowering context
- Return-type inference: `"str"` symbol-table entries (regular Python `str` params) map to `int`; ghost string vars are `_ghost_string_vars` tracked separately — no conflict

---

## Deferred Work (Phase 3)

### E1. End-to-end proof tests for ghost types

All reference tests (0292–0300) use `--no-proof`. Full SMT proofs for ghost types are not yet validated. Priority order (easiest first):

1. **Ghost int** — should already work (pre-existing tests)
2. **Ghost tuple** — `(a, b)` tuples in Why3 are native; Z3 handles them well
3. **Ghost list** — `List.length` and `\cons`-based invariants are tractable
4. **Ghost dict** — `Map.get`/`Map.set` axioms are in Z3; complex chains may timeout

Create `0301.py` through `0307.py` as provable variants (without `--no-proof`).

### E2. `\set_union`/`\set_inter`/`\set_diff` Z3 validation

Test 0299 only uses `\set_add`. A dedicated test with `\set_mem(k, \set_union(s1, s2))` in a proof context is needed to confirm Z3 can discharge the obligation. The functional representation (λ k → ...) may confuse quantifier instantiation — consider using bounded ranges.

**Restriction to document:** "Restrict `\set_union`/`\set_inter`/`\set_diff` operands to bounded integer ranges for best SMT performance."

### E3. `\proj` arity mismatch negative test

Add XFAIL test:
- `\proj(p, 2)` where `p` is `tuple2` (index out of range) — should emit wrong WhyML but not crash
- `\proj(t, n)` where `n` is not a literal — should be caught by Module4 (already implemented)

### E4. Ghost string augmented assignment rejection

The `ghost_aug_assign` rule currently accepts `#@ ghost s += "x"` for a ghost string. This should be rejected at Module4 (string concat should use `^` operator, not `+=`). Add a XFAIL test and Module4 validation.

### E5. Ghost set `+=` shorthand

Analogous to `ghost_list += x` and `ghost_dict += \mktuple(k, v)`:
- `#@ ghost s += x` as shorthand for `#@ ghost s = \set_add(s, x)`
- Module6: add `if op == "+=" and ghost_type == "ghost_set"` branch

### E6. `\map_eq` in loop invariants

`\map_eq(d1, d2)` emits a `forall` quantifier. Verify Z3 handles this in a loop invariant context. Add a `--no-proof` test first, then a full proof test.

### E7. Transpiler limits documentation update

Update `references/transpiler-limits.md` with a table:

| Ghost type | Required `use` | Notes |
|---|---|---|
| `string` | `string.String` | `^`, `\str_length`, `\str_sub` |
| `array` | `array.Array` | hoare/concurrent only |
| `ghost_dict` | `map.Map`, `map.Const` | `\map_eq` uses `forall` |
| `ghost_list` | `list.List`, `.Length`, `.Nth`, `.Mem`, `.Append` | |
| `ghost_set` | `map.Map`, `map.Const` | set ops are functional lambdas |
| `tuple2/3/4` | none | native Why3 tuples |

---

## Recommendations for Phase 3

1. **Prioritize E1** — full proof tests establish that the WhyML generated is actually correct, not just parsable. Start with `ghost_tuple` (simplest) and work up.

2. **Add E5 (ghost set `+=`)** — consistent with D4/D6 shorthands; low effort.

3. **Validate `\set_union` with Z3 (E2)** before using it in agent-generated annotations — functional lambda representation in Why3 axioms is less well-supported than `Map.get`/`Map.set` chains.

4. **Run self-annotation pipeline on Module6** — now that all 5 module self-annotated copies are synced, re-running the self-annotation pipeline on `Module6_WhyMLTranspiler.py` would generate improved contracts. The current `#@ requires 1 == 1` placeholders in Module6 can be replaced.

5. **Rebuild RAG** after any further skill updates — `./bin/update-rag.sh`.

---

Once the plan is done, provide recommendations and draft a new plan in `./src/self-annotate/plan-ghost-recommendation-??.md` where ?? is a new number compared to existing ones.
