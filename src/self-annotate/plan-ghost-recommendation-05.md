# Ghost Variable Types — Post-Implementation Recommendations (Phase 5)

## Completed Work (Session 10)

All H1–H6 items are done. Test suite stands at **319/321** (2 pre-existing failures: 0290, 0291).

| Item | Description | Status |
|------|-------------|--------|
| H1 | Ghost tuple4 proof test | ✅ (0319) |
| H2 | Ghost list `\list_length` proof test | ✅ (0318) |
| H3 | Ghost string `^` proof test | ✅ (0321) — required bug fix: `concat` not `String.(^)` |
| H4 | `\proj` negative test | ✅ (0317_proj_dynamic_index) — already implemented in Module4 |
| H5 | `\has_key(d, k)` construct | ✅ (0320) — full pipeline + proof |
| H6 | Ghost list `\append` proof test | ✅ (0322) — required bug fix: typed `Nil` |

New reference tests: 0317 (XFAIL), 0318, 0319, 0320, 0321, 0322.

### Coverage summary after session 10

| Ghost type | --no-proof test | Proof test | Notes |
|---|---|---|---|
| `int` (standard ghost) | 0290 (XFAIL) | — | Pre-existing failure |
| `string` | 0295 | 0321 | `^` concat (`concat` function) proven |
| `array` | 0293 | 0313, 0315 | `\make`, `\copy` proven |
| `ghost_dict` | 0296 | 0310, 0311, 0320 | `Map.get/set`, `\map_eq`, `\has_key` proven |
| `ghost_list` | 0297 | 0312, 0314, 0318, 0322 | `\nth`, `\mem`, `\list_length`, `\append` proven |
| `ghost_set` | 0298 | 0308 | `\set_mem` after add/remove proven |
| `tuple2` | 0300 | 0307 | `\fst`, `\snd` proven |
| `tuple3` | 0301 | 0309 | `\proj(t,0/1/2)` proven |
| `tuple4` | 0302 | 0319 | all four projections proven |
| multi-type | 0316 | 0316 | dict+list+set proven |

---

## Bug Fixes in Session 10

### 10. `String.(^)` → `concat` in ghost string concatenation

**Problem**: `_handle_strconcat_expr` emitted `(String.(^) l r)`. Why3's `string.String` module
exports `concat` as the concatenation function, not `(^)` or `String.(^)`.

**Fix**: Changed to `f"(concat {l} {r})"` in all 3 Module6 copies.

### 11. `(Nil: list int)` for unused ghost list vars

**Problem**: `let ghost b = ref Nil in` — when `b` is never assigned integer values,
Why3 can't infer the type as `list int`. This causes a type mismatch when `b` appears
in `\append(a, b)` alongside a typed `a: list int`.

**Fix**: When the initial value of a `ghost_list` declaration is `Nil`, emit
`(Nil: list int)` to give Why3 an explicit type annotation. Applied to all 3 Module6 copies.

---

## Phase 5 Work Items (H1–H6)

### H1. Ghost tuple4 proof test

**Priority**: Low. Completes coverage for all tuple arities.

Create test `0317.py` using `tuple4` with all four projections (`\proj(t, 0..3)`) in
a loop invariant, proven with full Alt-Ergo proof.

Pattern:
```python
#@ ghost t : tuple4 = \mktuple(0, 0, 0, 0)
#@ loop invariant \proj(t, 0) == i
while i < n:
    #@ ghost t = \mktuple(i + 1, i + 1, i + 1, i + 1)
    i = i + 1
```

Expected: Alt-Ergo proves via tuple-destructure axioms (same mechanism as 0309).

---

### H2. Ghost list `\list_length` proof test

**Priority**: Medium. `\list_length` is not yet proven in any existing test.

Create test `0318.py` using `\list_length(log) == i` as loop invariant:

```python
#@ ghost log : ghost_list = \nil
i = 0
#@ loop invariant 0 <= i and i <= n
#@ loop invariant \list_length(log) == i
#@ loop variant n - i
while i < n:
    #@ ghost log += i
    i = i + 1
```

**Feasibility check needed**: `\list_length` maps to `List.length`. Why3's `list.Length`
exports `length: list 'a -> int` with lemma `Length_Cons: forall x l. length (Cons x l) = length l + 1`.
Alt-Ergo should prove `length (Cons i !log) = !i + 1` in one step via `Length_Cons`.

This is simpler than `\nth` (no index argument) so OOM is unlikely.

**If it fails**: Fall back to `\list_length(log) >= 0` which is always provable.

---

### H3. Ghost string `^` proof test ✅ DONE

**Bug found**: `_handle_strconcat_expr` emitted `(String.(^) l r)` but Why3's `string.String`
exports `concat` (not `(^)`). Fixed to `f"(concat {l} {r})"` in all 3 Module6 copies.
Also: string literals were already supported via `ESCAPED_STRING` terminal.

Test 0321 proves `\str_length(s) == i` with `ghost s = s ^ "x"` update. ✅

---

### H4. `\proj` static validation (hard error for non-literal index) ✅ DONE

**Finding**: `_validate_proj_indices` was already implemented in Module4 and all 3 copies
(sessions 7–9). Only the negative reference test was missing.
```python
# pycsl-expected: FAIL
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def bad_proj(t: tuple, i: int) -> int:
    #@ ghost q : tuple2 = \mktuple(0, 0)
    #@ loop invariant \proj(q, i) == 0
    #@ loop variant 1
    while 0 == 1:
        pass
    return 0
```

Test 0317 (renamed from `0317_proj_dynamic_index.py` to `0317.py` for compatibility with
numeric test runner). ✅

---

### H5. `\has_key(d, k)` construct ✅ DONE

Implemented in Module2 (grammar + `HasKeyExpr` dataclass + transformer), Module4 (`_CSL_CHILDREN_MAP`),
Module5 (`_csl_has_key`), Module6 (`_handle_has_key_expr` + `HasKey` in `_to_bool` bypass).
Applied to all 3 self-annotated copies. Emits `(Map.get !d k <> 0)` (sentinel-0 convention).

Test 0320 proves `i > 0 ==> \has_key(d, 0)` combined with `\map_get(d, 0) == i`. ✅

---

### H6. Ghost list `\append` proof test ✅ DONE

**Bug found**: `let ghost b = ref Nil in` — `Nil` is polymorphic; Why3 can't infer `list int`
when `b` is never used with integer ops. Fixed: when initial value is `Nil`, emit `(Nil: list int)`.

Test 0322 proves `\list_length(\append(a, b)) == i` (using `list.Length` + `list.Append`).
Alt-Ergo discharges via `Length_Cons` lemma in one step. ✅

---

## Verification (Session 10 Results)

```bash
# All 12 modified files compile cleanly:
python3 -m py_compile src/pycsl/Module{2,4,5,6}_*.py
python3 -m py_compile src/self-annotate/rocq/Module{2,4,5,6}_*.py
python3 -m py_compile src/self-annotate/lean/Module{2,4,5,6}_*.py

# New tests individually:
# 0317: exits 1 (XFAIL — \proj index must be integer literal)
# 0318: Verification SUCCESS (list_length proof)
# 0319: Verification SUCCESS (tuple4 proof)
# 0320: Verification SUCCESS (\has_key proof)
# 0321: Verification SUCCESS (string concat proof)
# 0322: Verification SUCCESS (\append proof)

# Full test suite: 319/321 passed
```

---

## Skill Files Updated

| Skill file | What was added |
|---|---|
| `pycsl-annotate/SKILL.md` | `\has_key(d, k)` in ghost dict atom list |
| `contract-writer/SKILL.md` | `\has_key`, `\append` + `\list_length` atoms; string `concat` correction |
| `invariant-writer/SKILL.md` | `\list_length(\append(l1, l2))` pattern example |
| `pycsl-how-to-develop/SKILL.md` | `concat` not `String.(^)`; typed Nil; `\has_key` sentinel caveat |
| `test-suite/annotations.md` | `\has_key` in ghost dict table; string `^` emits `concat` note |
| `test-suite/traceability-pycsl.md` | Rows 0314–0322 added |

RAG rebuilt via `./bin/update-rag.sh`.

