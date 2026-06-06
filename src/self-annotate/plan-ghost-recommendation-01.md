# Ghost Variable Types — Post-Implementation Recommendations

## Completed Work (Sessions 1–2)

All 6 ghost variable types are now implemented end-to-end:

| Type | Grammar | Module4 | Module5 | Module6 | Tests |
|------|---------|---------|---------|---------|-------|
| `int` (default) | ✅ (was done) | ✅ | ✅ | ✅ | pre-existing |
| `string` | ✅ | ✅ | ✅ | ✅ | 0292 |
| `array` | ✅ | ✅ | ✅ | ✅ | 0293 |
| `ghost_dict` | ✅ | ✅ | ✅ | ✅ | 0294 |
| `ghost_list` | ✅ | ✅ | ✅ | ✅ | 0295 |
| `ghost_set` | ✅ | ✅ | ✅ | ✅ | 0296 |
| `tuple2/3/4` | ✅ | ✅ | ✅ | ✅ | 0297 |

Self-annotated copies (rocq/lean) updated for Module2, Module3, Module4, Module5.
Module6 rocq/lean copies retain old integer-only ghost path (deferred below).

---

## Deferred Work (Phase 2)

### D1. Module6 self-annotated copy full sync

The `src/self-annotate/rocq/Module6_WhyMLTranspiler.py` and lean copy need:
- `uses_ghost_type` added to `IRScanner`
- `_ghost_*_vars` added to `_reset_function_state`
- All 28 ghost expression handler methods (`_handle_mktuple_expr`, etc.)
- Updated `_EXPR_DISPATCH` ghost entries
- Updated `_scan_preamble_needs` ghost flags
- Updated `_emit_preamble_uses` ghost library `use` declarations
- Updated `_handle_ghost_assign_stmt` with ghost_type dispatch
- `_handle_ghost_array_set_stmt`
- `_expr_to_whyml_string_ctx`

**Priority**: Medium. The self-annotated copies generate incorrect WhyML for ghost types
but do not crash. Re-run self-annotation pipeline on Module6 after this sync.

### D2. Ghost string `\str_length` and `\str_sub` builtins

From ghost-string-final.md Phase 6 (explicitly deferred):
- `\str_length(s)` → `String.length !s`
- `\str_sub(s, lo, hi)` → `String.sub !s lo (hi - lo)`

Requires grammar addition, Module5 IR handler, Module6 emit.

### D3. Secondary Module6 touch-point audit for ghost strings

From ghost-string-final.md §5f:
- `_coerce_str_arg`: must not coerce ghost string variables to `int`
- `_handle_fstring_expr`: ghost strings must not participate in f-string lowering
- Return-type inference: `"str"` scope annotation must not produce wrong WhyML types

### D4. `\map_get` / `\map_set` augmented assignment shorthand for ghost dicts

From ghost-dictionnaries-final.md:
- `#@ ghost freq += (key, val)` shorthand for `\map_set`
- Module2 grammar: `ghost_dict_aug: "ghost" CNAME "+=" "(" expr "," expr ")"`

### D5. `\set_union`, `\set_inter`, `\set_diff` Z3 validation

From ghost-sets-final.md §D5:
- A reference test confirming Z3 handles `\set_mem(k, \set_union(s1, s2))` is needed
  before Phase 2 is declared complete.
- Document: "Restrict union/inter/diff operands to bounded integer ranges for best SMT
  performance."

### D6. `ghost_list += x` shorthand

From ghost-lists-final.md:
- `#@ ghost log += x` as shorthand for `#@ ghost log = \cons(x, log)`
- Requires Module4 to detect this and rewrite before IR emission.

### D7. Ghost tuple `\proj` performance

The current `\proj(t, i)` implementation generates `let (_, _, z_, ...) = !t in z_`
which requires the arity from `_ghost_tuple_vars[var]`. Verify this works correctly
for indices at the boundary of tuple arity (e.g., `\proj(t, 1)` for tuple2).

### D8. RAG index rebuild

After any skill file updates, run:
```bash
./bin/update-rag.sh
```
The skill files were updated in this session:
- `config/skills/pycsl-annotate/SKILL.md`
- `config/skills/contract-writer/SKILL.md`
- `config/skills/invariant-writer/SKILL.md`

---

## Recommendations for Phase 2

1. **Prioritize D1** — self-annotated Module6 sync is a technical debt that grows with
   each new ghost-type annotation session.

2. **Add end-to-end proof tests** — the current reference tests (0292–0297) all use
   `--no-proof`. Create provable variants once the SMT performance of each ghost type
   is confirmed (start with ghost integers and tuples, which should be easiest).

3. **Add negative tests** — add XFAIL tests for:
   - Dynamic `\proj` index: `\proj(t, n)` where `n` is not a literal
   - Wrong arity: `\proj(p, 2)` where `p` is `tuple2`
   - Augmented assignment on string ghost: `#@ ghost s += "x"` (should be rejected)

4. **Benchmark ghost dict/set with Z3** — `map int bool` and `map int int` are
   theoretically supported by Z3's theory of arrays, but complex invariants involving
   `\map_set` chains may timeout. Run the annotation pipeline on a hash-counting
   algorithm to validate.

5. **Document WhyML preamble dependencies** — update `references/transpiler-limits.md`
   with a table of which ghost types trigger which `use` declarations, so agents know
   what dependencies exist.

---

Once the plan is done, provide recommendations and draft a new plan in `./src/self-annotate/plan-ghost-recommendation-??.md` where ?? is a new number compared to existing ones.