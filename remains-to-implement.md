# remains-to-implement.md — Data-structure modelling in Module6

Status: Open backlog
Date: 2026-05-26
Companion: [`my-llm-is-lazy.md`](my-llm-is-lazy.md) (the original audit + plan).

## What landed this session

Phases 1–3 of `my-llm-is-lazy.md`, plus the small wins from Phase 4
(Bucket B). Every change comes with a regression-clean reference suite
(0342, 0331, 0341, 0343, 0344 all SUCCESS under full proof; 162/5/0
audit; `make self-annotate-verify` all green).

| # | Item | Status |
|---|---|---|
| Body `dict`s → `map.Map (option int)` | Phase 1 | ✅ shipped |
| `dict_new()` / `DictLit` emit `(const (None: option int))` | | ✅ |
| `_handle_subscript` for dict locals → `match Map.get …` | | ✅ |
| `_handle_array_set_stmt` for dict locals → `Map.set` | | ✅ |
| `_handle_binop` `in` / `not in` on dict locals → `Map.get … <> None` | | ✅ |
| `_emit_preamble_uses` imports `map.Map`, `map.Const`, `option.Option` when any body dict | | ✅ |
| Body `set`s → `map.Map`-based (lite Phase 2) | Phase 2 | ✅ shipped |
| `set()`/`frozenset()` and `SetLit` emit map-based | | ✅ |
| `s.add(x)` / `s.discard(x)` / `s.remove(x)` as statements → `Map.set` | | ✅ |
| (`in` already works via Phase 1 — sets ride the dict path) | | ✅ |
| `Optional[T]` / `Union[T, None]` return-annotation extraction | Phase 3 | ✅ shipped |
| `sorted(arr)` builtin → abstract `sorted_1 : array int → array int` | | ✅ |
| `any(iter)` / `all(iter)` builtins → abstract `: bool` | | ✅ |
| Multi-arg `range(start, stop)` for `for i in range(s, e)` | Phase 4 | ✅ shipped |

**Cumulative transpiler fixes across the session**: now 22 distinct
Module6/Module5 bugs removed. Self-annotated Module6 progresses past
classes M, O, P, Q, R (dicts), and now also handles sets / multi-arg
range / sorted / Optional.

## What remains

### Bucket B — still open

| Item | Why deferred | Suggested approach | Effort |
|---|---|---|---|
| **Comprehensions** (`ListComp`, `DictComp`, `SetComp`) | Non-trivial desugar; needs accumulator + for-loop emission at the Module5 IR level. Currently emit opaque `val list_comp / dict_comp / set_comp : int`. | Lower at Module5: `[expr for x in iter if cond]` → a hidden function that returns the list. Or: emit a fresh local `_lc_<id> = [] ; for x in iter: if cond: _lc_<id>.append(expr)` directly into the parent statement list. The latter is simpler if Module5 can rewrite the statement context. | 1–2 days |
| **`enumerate(seq)`** as iter source | `_classify_iterable` doesn't recognise Call expressions other than `range`. | Special-case `iter_ir.get("func") == "enumerate"`: treat as range over `Array.length seq` with the target being a 2-tuple `(idx, seq[!idx])`. Requires tuple-target support in for-loops, which Module6 may not handle yet. | ½–1 day |
| **`zip(a, b)`** as iter source | Same shape as `enumerate` but two parallel arrays; iter target is a 2-tuple. | Similar special-case in `_classify_iterable`: `Array.length a` (or min of two lengths), target `(a[!idx], b[!idx])`. | ½–1 day |
| **`map(f, seq)`** / **`filter(f, seq)`** | Higher-order; cannot apply `f` without runtime lambda. | Probably not worth modelling — rewrite as comprehension/loop. Document loudly. | not recommended |
| **Lambdas in body code as callable values** | `_lambda_locals` tracks them but `(lambda x: …)(arg)` isn't a recognised call shape. | Substitute lambdas inline at call sites (Module5 pass), or refuse (and document) lambdas escaping ghost contexts. | 1 day or "forbidden" |
| **Empty/full set/dict identity** (`d == {}`, `len(d)`) | `len()` on a body dict currently has no handler; `==` falls into the generic comparison. | `len(d)` → `Fset.cardinal` for sets is appealing but the current model is `map int (option int)` which doesn't expose cardinality without a custom predicate. Simplest: emit an abstract `val map_size (m: map int (option int)) : int`. `==` between dicts: emit a `forall k. Map.get a k = Map.get b k` quantifier (parallel to `\map_eq`). | ½ day |

### Class R subset — dict-of-array still open

Phase 1 models `Dict[*, int]`. The cascade error in `_handle_subscript`
(class R) was about `Dict[str, List[int]]` patterns like
`known_elems[var_name]` where the value is an array. Module6 still
collapses the value to `int`. Fix would require parametric dict
modelling — `map int (array int)` — and threading the value type
through the IR. Estimated effort: 1 day.

### Caught exception value (`except E as e:`)

`e` is parsed by Module5 (IR field `exc_var`) but ignored by Module6's
`_handle_try_stmt`. If a handler body references `e.args` or similar,
Module6 falls back to `getattr_*` abstract vals → opaque int. Not
load-bearing; PyCSL's own source re-raises rather than inspecting `e`.
Documenting that `e` is unbound in handler bodies would be enough.

### Bucket C — confirmed out of scope, no work planned

- `bytes` / `bytearray`
- `re.Match` / `re.Pattern` (regex)
- NumPy arrays
- Generators / `yield` / iterator protocol
- External library types (LibCST, AST, Path, etc.)

These remain opaque `int` by design. See `my-llm-is-lazy.md` § "On the
LLM is lazy framing" for the rationale.

## Layer-2 self-annotation impact

With Phases 1–3 + the small Bucket B win, the Module6 self-annotated
file should advance through several previous blocker classes
automatically. The "auto-trusted" lists
(`_auto_trusted_array_returns`, `_auto_trusted_tuple_returns`)
ideally shrink — though some entries reflect deeper issues than just
dict/set modelling (e.g. heterogeneous tuple slot types).

The frontier of `pycsl src/self-annotate/src/Module6_WhyMLTranspiler.py`
under full proof is now expected to be a NEW class — likely one of:

- Comprehension lowering (if a `[x for x in …]` slips through).
- The `Dict[*, list]` heterogeneous-value subset of class R.
- A new class entirely (Module6 has 3617 lines of code; not every
  emission shape has been exercised yet).

Re-running `pycsl --keep-mlw` on the self-annotated Module6 after this
session's work would surface the new frontier. That's the natural
next step before tackling any item in the table above.

## Risks / things to watch

- **Performance**: `map.Map` operations involve quantifier reasoning.
  No regression observed on 0342 (still 0.01–28 s range), but watch
  the dict-heavy reference tests (0294, 0300, 0307, 0311, 0316) if
  they ever move from `--no-proof` to full proof.
- **`set` and `dict` share the same emission path** in Module6 now
  (both map to `map int (option int)`). This works because Python's
  set is morally a dict-with-no-values. If we later want `Fset.fset`
  for true set semantics (with `Fset.cardinal`, set comprehensions
  etc.), we'd need to split `_set_locals` out of `_dict_locals`. The
  current `IRScanner.find_array_and_dict_vars` already conflates them
  (line 120-121).
- **`Union[T1, T2]` with heterogeneous T1, T2**: Phase 3 picks the
  first non-`None` component as a heuristic. `Union[int, str]` would
  return `"int"` — correct only by accident. For PyCSL's own code this
  doesn't bite, but document the limitation if it ever does.
- **`Optional[T]` collapses to T**: we model `None` as `0`, so the
  Optional-ness adds no type-level info. Code that distinguishes
  `None` from the zero value (e.g. `if x is not None:`) is already
  handled via `transpiler-limits.md` IS-1 (rewrite as `x != 0`).

## Recommended next session

1. Re-run `pycsl --keep-mlw src/self-annotate/src/Module6_WhyMLTranspiler.py`
   to identify the new frontier blocker.
2. If the blocker is a comprehension: tackle the comprehension
   desugaring (~1.5 days).
3. If the blocker is `Dict[*, list]`: extend dict modelling to track
   value types per-key (~1 day).
4. Otherwise: triage the new blocker class against the queue in
   `docs/self-annotate-layer2-queue.md` and add an entry.
