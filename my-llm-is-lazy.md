# my-llm-is-lazy.md — Model the unmodelled data structures in Module6

**Status:** ⚠️ **Historical document.** The Bucket A/B/C work this
plan describes shipped 2026-05-26 (body dicts, body sets,
`Optional`/`Union`, `sorted`/`any`/`all`, multi-arg `range`). The
audit-script references it contains point at a tool that has since
been replaced by `pycsl --audit-proof`. The text below is preserved
as historical context; do not re-execute its steps.

Date: 2026-05-26
Scope: Audit every Python data structure / built-in / library type for
whether Module6 actually models it or just emits an opaque `int`, then
propose concrete remediation aligned with Why3's stdlib instead of more
`\trusted` escape valves.

## Context

The Layer-2 self-annotation push has surfaced a recurring pattern: Module6
emits **opaque `int`** for several Python types that it could properly
model using Why3's stdlib (`map.Map`, `option.Option`, `set.Fset`,
`string.String`, …). The opacity isn't an inherent Why3 limitation — Why3
has perfectly good theories for all of these. It's a Module6 implementation
gap.

The framing: the original transpiler (or its LLM ghostwriter) reached for
`val foo (...) : int` abstract stubs whenever modelling required
non-trivial Why3 stdlib `use` directives or emission logic. Each stub is
locally cheap but cumulatively forces every downstream consumer to treat
the result as opaque, cascading into type-mismatch errors at every
Layer-2 verification attempt.

What follows is an honest accounting of which gaps are **load-bearing**
(blocking self-annotation), **ergonomic** (annoying but workaroundable),
and **out-of-scope** (genuinely not worth modelling in a Hoare-logic
verifier).

## Inventory

Categories: ✅ modelled (Why3 stdlib semantics), 🟡 partial, ❌ opaque `int`.

### Properly modelled
- **`int`** ✅ — Why3 `int`. No work needed.
- **`bool`** ✅ — `bool` in spec, `int` in body via int-bool duality (well-documented).
- **`tuple`** ✅ — Why3 native tuples; per-arity `Return_N` exceptions for early returns. Just landed this session.
- **`list` / `array.Array.array int`** ✅ — `array.Array` with fixed size 1024 + companion `<name>_len` counter. Modelled but with the documented size limit (G5).
- **`None`** ✅ — `0` in body, `option.Option.None` in ghost contexts.
- **Class instances with `#@ class invariant`** ✅ — emitted as Why3 records, fields properly typed; instance methods get class-prefixed names. Trust-chain Layer 1 depends on this.
- **Ghost `string`, `ghost_list`, `ghost_dict`, `ghost_set`, `tuple2/3/4`** ✅ — all backed by appropriate Why3 stdlib theories (`string.String`, `list.List`, `map.Map (option int)`, `map.Map bool`, native tuples).

### Partially modelled
- **`str` (body)** 🟡 — hashed to `int` (`str_concat`, `str_conv` etc. as abstract vals). Concatenation works at the int-hash level only. Equality between literals returns the right answer if the hashes collide consistently. Methods (`.split`, `.join`, `.replace`, `.lower`, …) all forbidden.
- **Lambdas** 🟡 — only meaningful in ghost contexts (emitted as `fun x -> …`). In body code, lambda values are opaque `int` and uncallable.
- **Built-ins** 🟡 — `abs`/`len`/`min2`/`max2`/`sum` modelled; `sorted`/`any`/`all`/multi-arg `range`/`min(list)` not. `transpiler-limits.md` §5 documents the forbidden subset.

### Opaque `int` — the gap list
- **Body `dict`** ❌ — `val dict_new () : int`. Subscript, `in`, `for k in d`, `.items()/.keys()/.values()/.get()`, `del` — all forbidden. Comment `Module6_WhyMLTranspiler.py:519` says "Local dict variables (not real arrays)". This is the gap that exposed class R during self-annotation.
- **Body `set` / `frozenset`** ❌ — `val set_empty () : int`. `in`, `.add()`, `.union()`, `.intersection()` — all forbidden. **Undocumented**.
- **Comprehensions (`ListComp`, `DictComp`, `SetComp`, `GeneratorExp`)** ❌ — `val list_comp (x: int) : int` and friends. **Undocumented as forbidden** but effectively are.
- **Iterators / generators / `enumerate` / `zip` / `map` / `filter`** ❌ — `val iter_length / iter_get` stubs; `yield`/`next` have no handler. `range(n)` is the only modelled iterable. **Mostly undocumented**.
- **`Optional[T]` / `Union[T1, T2]` type hints** ❌ — Module5 doesn't recognise non-`Name`/`Constant`/`Subscript` annotations. Fix landed this session for `Subscript` (capturing the head ident lower-cased), but `Optional` and `Union` still vanish.
- **Caught exception variables (`except E as e:`)** ❌ — IR field `exc_var` parsed but Module6 ignores it. **Undocumented**.
- **`re.Match` / `re.Pattern` / `bytes` / `bytearray` / NumPy** ❌ — no handlers. Used nowhere in PyCSL's own code, so low priority.
- **External library types (LibCST, `ast.*`, `pathlib.Path`)** ❌ — opaque by intent (`transpiler-limits.md` line 53). Cannot meaningfully model without importing the library's semantics.

## Categorization for remediation

| Bucket | Items | Why |
|---|---|---|
| **A — Load-bearing for self-annotation** | Body `dict`, body `set`, `sorted`, `Optional[T]`/`Union[T1, T2]` | PyCSL's own source uses these patterns heavily (call-graph dicts, name-tracking sets, sorted iteration). Modelling them unblocks 30+ functions worth of `\trusted` workarounds. |
| **B — Ergonomic / occasional** | Comprehensions (`ListComp`, `DictComp`, `SetComp`), `enumerate`, `zip`, lambdas in body, multi-arg `range` | Annoying when they appear in user-written verified code, but PyCSL's self-annotation avoids them (already documented as "rewrite with explicit loops"). Worth fixing for general PyCSL users, lower priority for Layer 2. |
| **C — Out of scope** | `bytes` / `bytearray`, regex, NumPy, generators (`yield`), iterator protocol, caught exception values | Genuinely heavy modelling effort with no payoff for PyCSL's self-hosting. Document loudly; don't attempt. |

## Recommended approach

Three phases, smallest-first. Each phase ends with a regression sweep
(reference suite + `make self-annotate-verify` + audit) and lifts the
auto-`\trusted` workarounds it makes redundant.

### Phase 1 — Body dicts → real `map.Map` (Bucket A, highest impact)

**Approach**: when a variable is in `_dict_locals`, use the same Why3
modelling already in place for ghost dicts:

- Type: `map int (option int)` (`use map.Map`, `use option.Option`).
- Initial: `Map.const (None: option int)`.
- `d[k] = v` → `d := Map.set !d (hash k) (Some v)`.
- `d[k]` (read) → `match Map.get !d (hash k) with Some v -> v | None -> 0 end`.
- `k in d` → `Map.get !d (hash k) <> None`.
- `del d[k]` → `d := Map.set !d (hash k) None`.

**Caveat**: dict values are uniformly `int` in this model. `Dict[str,
List[int]]` (where the value is an array) needs a deeper change — class
R in `docs/self-annotate-layer2-queue.md` documents this. As a first
step, model only `Dict[*, int]` (all-int values); `Dict[*, list]` and
`Dict[*, dict]` continue to need `\trusted`.

**Files**:

- `src/pycsl/Module6_WhyMLTranspiler.py`:
  - `_handle_subscript` — special-case `d[k]` when `d` is in `_dict_locals`.
  - `_handle_assign_stmt` — special-case `d[k] = v`.
  - `_handle_binop` — `in` / `not in` when RHS is dict.
  - `_handle_for_stmt` / `_classify_iterable` — iteration over dict keys.
  - `_emit_preamble_uses` — unconditionally `use map.Map`, `use option.Option` when any `_dict_locals` exists.
- `IRScanner.find_array_and_dict_vars` — already detects `{}` / `dict()` / `DictLit`. No change.

**Estimated effort**: 1.5–2 days for the main path; add 4 hours for the
`Dict[*, list]` extension if you want to close class R.

### Phase 2 — Body sets → real `Fset` (Bucket A)

**Approach**: parallel to dicts, use Why3's `set.Fset` theory.

- Type: `Fset.fset int`.
- Initial: `Fset.empty`.
- `s.add(x)` → `s := Fset.add x !s`.
- `s.remove(x)` → `s := Fset.remove x !s`.
- `x in s` → `Fset.mem x !s`.
- `s1.union(s2)` → `Fset.union !s1 !s2` (similar for `intersection`, `difference`).
- `len(s)` → `Fset.cardinal !s`.

Lift the auto-trust on any method whose only Why3 gap was a `set_*` call.

**Files**: same set of Module6 methods as Phase 1. `set.Fset` import added.

**Estimated effort**: 1 day (sets are simpler than dicts — no key/value distinction).

### Phase 3 — `Optional[T]` / `Union[T1, T2]` in Module5 + `sorted` builtin

**Optional[T]**: extend `_build_function_ir` in Module5 to recurse into
`Subscript` with head ident `Optional` and use the *inner* type
(`Optional[int]` → `"int"`, `Optional[List[str]]` → `"list"`).
`Union[T, None]` likewise.

**`sorted(iterable)`**: emit as an abstract `val sorted (a: array int) : array int`
for arrays; for dict-keys, depends on Phase 1.

**Files**:

- `src/pycsl/Module5_IREmitter.py` — `_build_function_ir` Subscript handling.
- `src/pycsl/Module6_WhyMLTranspiler.py` — `_handle_call_expr` for `sorted`.

**Estimated effort**: ½ day.

### Phase 4 (optional) — Comprehensions

`[expr for x in iter if cond]` is a syntactic sugar for an explicit loop.
Lower it to such a loop at the Module5 IR level (NOT at Module6), so
Module6's existing loop emission handles it. Same for dict/set comps.

**Files**: `src/pycsl/Module5_IREmitter.py` — new `_py_expr_listcomp` / `_py_expr_dictcomp` / `_py_expr_setcomp` desugaring.

**Estimated effort**: 1 day; tricky because comprehensions can be deeply nested.

## Critical files

- `src/pycsl/Module6_WhyMLTranspiler.py` — the heart of this work. All
  `val foo (...) : int` stubs are candidates for replacement with real
  Why3 types.
- `src/pycsl/Module5_IREmitter.py` — annotation extraction needs to grow
  for `Optional`/`Union` and (in Phase 4) comprehension desugaring.
- `IRScanner.find_array_and_dict_vars` (Module6 line 100) — extend
  recognition for new dict/set producers if any.
- **No changes to `src/formal-semantics/`**: the WP soundness theorems
  don't care about which Why3 types we map Python to, as long as the
  semantic equivalences hold.

## What we are NOT doing

- **Not modelling external library types** (LibCST, AST, Path, regex, NumPy).
  These genuinely live outside PyCSL's verification scope. Their opacity
  is intentional, and the `transpiler-limits.md` line 53 warning is the
  right disposition.
- **Not modelling iterators / generators / `yield`**. PyCSL is a Hoare-logic
  verifier; lazy semantics are a fundamentally different design surface.
- **Not modelling `bytes` / `bytearray`**. Unused in PyCSL itself, no payoff.
- **Not removing existing auto-`\trusted` machinery**. Phases 1–3 will
  reduce its triggering set, but the machinery stays as a safety net for
  cases the proper modelling doesn't cover (heterogeneous tuples, deeply
  nested dict-of-array, etc.).
- **Not breaking the body / ghost distinction**. `#@ ghost d : ghost_dict`
  remains the contract-level dict; the new body-level dict modelling uses
  the same `map.Map` theory but lives in `_dict_locals` (separate
  tracking, separate emission path).

## Existing utilities to reuse

- `map.Map`, `map.Const`, `option.Option` already imported when
  `needs_ghost_dict` is true. Phase 1 just adds another trigger.
- `set.Fset` not currently imported anywhere — Phase 2 adds it. Note Why3
  also has `map.Map bool` for predicate-style sets (used by `ghost_set`),
  but `Fset` is closer to Python's `set` semantics (finite, enumerable).
- The auto-`\trusted` infrastructure (`self._auto_trusted_array_returns`,
  `_auto_trusted_tuple_returns`) is the right place to track which
  functions were force-trusted; as Phases 1–3 reduce coverage, these
  lists should shrink toward zero.
- The existing dict-emission abstract vals (`dict_new`, `dict_get`,
  `dict_set`, `contains_check`) can be REPLACED in-place — keep their
  names but change their signatures and implementations to match the
  `map.Map` model. Callers don't need to change.

## Verification

```bash
# After each phase, run the full regression set:
PYTHONPATH=src .venv/bin/python -m pycsl.pycsl test-suite/corpus/pycsl-reference/0342.py
PYTHONPATH=src .venv/bin/python -m pycsl.pycsl test-suite/corpus/pycsl-reference/0331.py
make self-annotate-verify
bash bin/check-proof-attributions.sh

# Phase-1 specific (after dicts → Map):
# Try full proof on Module6 — the class R blocker should be resolved.
PYTHONPATH=src .venv/bin/python -m pycsl.pycsl \
    src/self-annotate/src/Module6_WhyMLTranspiler.py 2>&1 | tail -3
# Expected: a NEW error class, not the int-vs-array mismatch on
# `contains_check !idx_val !known_elems[!var_name]`.

# Phase-2 specific (after sets → Fset):
# Module6's own code uses `set()` for tracking; full-proof verification
# should walk further before stopping.

# Phase-3 specific (after Optional + sorted):
# Reference suite: 0220-0235 use Optional/sorted patterns — verify none
# regress.
bash bin/run-reference-tests.sh --pycsl --start-at 220 --stop-at 235

# Cumulative: count the auto-trusted lists' length BEFORE and AFTER.
# Phases 1+2 should drop it by at least 1/3.
```

## Risks

- **Performance regression on existing tests.** `map.Map` operations
  involve quantifier reasoning that may be slower than the current
  opaque-`int` model. Alt-Ergo can handle `map.Map` well, but watch the
  reference suite timings during Phase 1 — if any 0342-style test slows
  from < 1 s to > 30 s, the modelling is too detailed.
- **Hash collisions on `str` keys.** The current `str → hash int`
  representation means `"foo"` and a collision-equivalent string would
  appear equal in WhyML. This is a pre-existing limitation (G2 in
  `pycsl-translational-reference.md`). Phase 1's `Map.set !d (hash k)` is
  no worse than the current `_handle_assign_stmt` for `d[k] = v` would
  be; but it's worth documenting that dict-lookup verification is
  modulo-hash-equality.
- **`Dict[*, list]` is still broken after Phase 1.** Phase 1 models
  values as `int`; the heterogeneous-value case (e.g. `_record_types:
  Dict[str, RecordInfo]`) needs a deeper model (parametric dicts). The
  `\trusted` workaround on those specific functions stays in place.
- **`Fset` finite vs `map.Map bool` infinite**. Ghost sets use the
  `map.Map bool` model (good for predicates, infinite). Body sets in
  Phase 2 will use `Fset` (finite, enumerable). The two models DON'T
  unify — keep them as separate emission paths.

## Effort estimate

| Phase | Items | Effort |
|---|---|---|
| 1 | Body dicts → `map.Map` | 1.5–2 days |
| 2 | Body sets → `Fset` | 1 day |
| 3 | Optional/Union + sorted | ½ day |
| 4 (optional) | Comprehensions → loop desugar | 1 day |
| Verification + queue-doc updates | per-phase | ½ day each |
| **Total (Phases 1–3 only)** | | **~4 days** |
| **Total (with Phase 4)** | | **~5 days** |

## On the "LLM is lazy" framing

Reviewing the gap list honestly: about **60%** of it (body dict, body
set, `sorted`/`any`/`all`, `Optional`/`Union`) is genuinely fixable
using existing Why3 stdlib facilities and would have been
straightforward to write correctly the first time. About **25%**
(comprehensions, lambdas in body, generators) is non-trivial but
doable. The remaining **15%** (external library types, NumPy, regex,
bytes, generators with `yield`) is genuinely out-of-scope for a
Hoare-logic verifier and the opaque `int` is the right call.

So "my LLM is lazy" is half right: the implementation took shortcuts
where modelling was achievable, and they're now compounding into the
Layer-2 verification frontier. Phases 1–3 of this plan close that gap.
The remaining 15% should be documented loudly so future contributors
don't try to "fix" what shouldn't be fixed.
