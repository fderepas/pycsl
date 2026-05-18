# PyCSL Python Subset — Extension Opportunities

## Context

PyCSL currently supports a subset of Python that covers pure functions, loops with
invariants, mutable class fields, and array operations. The gap analysis below identifies
what is missing and ranks each extension by verification value vs. implementation cost.
The ranking uses the pipeline touch-points: M2 = Module2_Parser, M3 = Module3_Weaver,
M5 = Module5_IREmitter, M6 = Module6_WhyMLTranspiler.

---

## Review notes (2026-05-18)

### On the 3-tier split

The split conflates two independent axes — *implementation difficulty* and *user value*
— into a single ranking. This works for Tier 1 (items that are both easy AND valuable)
but breaks down in Tiers 2 and 3:

- **Tier 2 is heterogeneous.** Item 8 (tuple unpacking) is mechanically simple (Why3 has
  native `let (a,b) = f() in`; M5 already handles `ast.Tuple` as an expression) and
  could be Tier 1 at ~1 day effort. Item 6 (walrus) genuinely needs new infrastructure
  (pre-statement buffer), so Tier 2 is correct. Item 9 is a trivial extension of item 1
  and barely warrants its own entry.

- **Tier 3 mixes "hard but valuable" with "do not implement."** Items 12 (generators)
  and 13 (async) are explicitly "not recommended" — they should be in a separate
  **Out of Scope** section, not ranked alongside real future work. Item 10 (match) is
  high-cost but arguably *high* value for modern Python (3.10+); item 11 (lambda) is
  genuinely lower value for verification. Lumping them all as "Medium value" is imprecise.

**Suggested restructuring:**

1. **Immediate** (< 1 day each, grammar-only or minimal): items 2, 3, 4
2. **Short-term** (1–3 days, straightforward pipeline additions): items 1, 8, 9
3. **Medium-term** (1 week+, new infrastructure needed): items 6, 7
4. **Long-term** (multi-week, research needed): items 10, 11
5. **Out of scope** (fundamentally incompatible with Why3): items 12, 13
6. **Ongoing** (parallelisable infrastructure, not a discrete feature): item 5

This separates the axes cleanly: rows 1–4 are ordered by cost, and within each row,
items are already filtered to "worth doing."

### Obsolescence notes

- **Item 4 (`in`/`not in`) is easier than stated.** M5 already maps `ast.In` →
  `"in"` and `ast.NotIn` → `"not in"` (line 136). M6 already handles both operators
  in body expressions (lines 588–613), including tuple expansion to `||`-chains and a
  `contains_check` fallback. The ONLY missing piece is the M2 contract grammar — this
  is a 1-day item, not 2 days.

- **Item 5 is partially obsolete.** The plan lists `hashlib` and `multiprocessing` as
  missing, but `data/lib_stubs/hashlib.py` and `data/lib_stubs/multiprocessing.py`
  already exist. Only `functools` and `itertools` remain.

- **Item 9 depends on item 1.** If item 1 is deferred, item 9 is moot. The "+1 day"
  estimate is correct but the two should be presented as a single item with an optional
  extension, not as separate tier entries.

### What the plan does well

- Correctly identifies that items 2, 3, 4 are grammar-only changes (M2) with near-zero
  risk to existing functionality.
- Correctly identifies that library stubs are independently parallelisable.
- The "not recommended" verdict on generators and async is sound — Why3's eager
  evaluation model is fundamentally incompatible.
- Touch-point analysis (which modules each feature needs) is accurate and useful for
  implementation planning.

---

## Tier 1 — High value, low cost (implement first)

### 1. `assert` statement → WhyML `check`

**Gap:** `ast.Assert` is silently dropped (treated as `Pass` in M5).  
**Value:** `assert cond` is a runtime check that belongs in the verified model as a proof
obligation. Why3 has a native `check` statement that works exactly this way — if the
solver cannot prove `cond` at that program point, the verification fails.  
**WhyML output:** `check { <condition> }`  
**Touch-points:** M5 (add `ast.Assert` case in `_py_stmts_to_ir`), M6 (add `"Assert"` IR
node → `check { expr }` emission).  
**Effort:** 1–2 days.

---

### 2. `//` and `%` in contract expressions

**Gap:** Floor division and modulo are forbidden in `#@` lines (grammar has no rule for
them). They already work in function bodies via `pycsl_div` / `pycsl_mod` wrappers.  
**Value:** Many loop invariants naturally involve modular arithmetic (e.g., even/odd
predicates, block-size alignment, hash-table proofs). The wrapper approach in the body
is already correct; contracts just need the same grammar rules.  
**WhyML output:** `//` → `div e1 e2`, `%` → `mod e1 e2` (EuclideanDivision library,
already imported in every module header).  
**Touch-points:** M2 (add `//` and `%` to `contract_expr` grammar, same precedence as
`*`/`/`), M5 (`_csl_to_ir`: `CSLBinOp` with `//`/`%` operators already handled — just
needs grammar), M6 (already emits `div`/`mod` for body; reuse for contracts).  
**Effort:** 1 day.

---

### 3. `True` / `False` / `None` literals in contracts

**Gap:** The contract grammar forbids bare Python booleans; annotators must write `1==1`
and `1==0`.  
**Value:** Eliminates a constant source of agent errors (the most common annotation
mistake). `True` maps to `true` in WhyML, `False` to `false`, `None` to a unit value or
a sentinel.  
**Touch-points:** M2 (add `True`, `False`, `None` as atoms in the grammar → emit
`CSLBool` node), M5 (`_csl_to_ir`: `CSLBool(True)` → `{"type":"BoolLit","val":true}`),
M6 (`_expr_to_whyml`: `BoolLit` → `true`/`false`).  
**Effort:** 1 day.

---

### 4. `in` / `not in` in contract expressions

**Gap:** `x in arr` and `x not in arr` have no grammar rule in M2 contracts.  
**Value:** Membership predicates appear in postconditions of search functions
(`\result in values`) and in invariants of set-based algorithms. Currently requires an
existential workaround: `\exists i; 0 <= i and i < \length(arr) and arr[i] == x`.  
**WhyML output (hoare):** `\exists i; 0 <= i /\ i < length arr /\ arr[i] = x`  
**Touch-points:** M2 only — M5 already maps `ast.In`/`ast.NotIn` to `"in"`/`"not in"`
operators (line 136), and M6 already handles both in body expressions (lines 588–613)
with tuple expansion and `contains_check` fallback. Only the M2 contract grammar needs
the new rule.  
**Effort:** 1 day (revised down from 2 — body support already complete).

---

### 5. Missing library stubs (`functools`, `itertools`)

**Gap:** Some standard library modules used in real Python code have no stubs.
Without stubs, calls to these modules produce `UnknownPyExpr` in M5.  
**Value:** Allows the pipeline to annotate real-world Python code that uses these
libraries. Stubs use `#@ \trusted` so no proof obligation is generated for the library
internals. English specifications are in `./test-suite/library_reference/`.  
**Touch-points:** `data/lib_stubs/` only — add one `.py` file per missing module
following the existing pattern.  
**Effort:** 1–2 days per module; independently parallelisable.  
**Priority order:** `functools` (reduce, partial, lru_cache), `itertools` (chain,
accumulate, combinations).  
**Note (2026-05-18):** `hashlib.py`, `multiprocessing.py`, and `xml` (via other stubs)
already exist in `data/lib_stubs/`. Removed from this list.

---

## Tier 2 — High value, medium cost

### 6. Walrus operator `:=` (`ast.NamedExpr`)

**Gap:** `x := expr` (Python 3.8+) returns `UnknownPyExpr` in M5.  
**Value:** The walrus operator appears in `while` guard conditions (`while chunk := f.read(1024)`)
and comprehension filters. Desugaring to an assignment + use is straightforward.  
**Desugaring:** `(x := e)` → emit `SAssign x e` before the containing expression, then
replace the `NamedExpr` with `EVar x`. Requires M5 to carry a "pre-statement" buffer that
flushes before the current statement.  
**Touch-points:** M5 (add `ast.NamedExpr` case: push assignment to pre-statement buffer,
return `EVar x`), M6 (no change — `Assign` + `Var` already handled).  
**Effort:** 3 days (the pre-statement buffer is new infrastructure).

---

### 7. Slice notation `arr[lo:hi]` in the function body

**Gap:** Slice objects appear in `ast.Subscript` nodes but are not lowered by M5
(only integer index subscripts are handled).  
**Value:** Slice-based operations (`arr[lo:hi]`, `arr[:n]`, `arr[i:]`) appear in sorting,
partitioning, and string-processing algorithms.  
**WhyML output:** `arr[lo:hi]` → introduce a ghost sub-array `sub` with
`\forall k; 0 <= k < hi-lo ==> sub[k] == arr[lo+k]`; the slice itself becomes the
ghost variable in contracts.  
**Touch-points:** M2 (add `arr[lo..hi]` as a contract atom for read-only views), M5
(lower `ast.Slice` inside `ast.Subscript` → new IR node `Slice {base, lo, hi}`), M6
(emit ghost sub-array + quantified equality).  
**Effort:** 1 week.

---

### 8. Multi-return tuple unpacking (`a, b = f()`)

**Gap:** `ast.Assign` with a `Tuple` target (e.g., `lo, hi = binary_search(arr, x)`) is
not handled — M5 only handles `ast.Name`, `ast.Attribute`, and `ast.Subscript` targets.  
**Value:** Many PyCSL-verified functions return multiple values (e.g., `(found, index)`,
`(lo, hi)`). Without this, callers must use `result[0]`, `result[1]`.  
**WhyML output:** `let (a, b) = f() in ...` — Why3 supports native tuple destructuring.  
**Touch-points:** M5 (add `ast.Tuple` target case in `_py_stmts_to_ir` → emit
`TupleUnpack {targets, value}` IR node), M6 (emit `let (<names>) = <expr> in`).  
**Note (2026-05-18):** M5 already handles `ast.Tuple` as an *expression* (line 206).
Adding it as an assignment *target* is mechanical. Arguably belongs in Tier 1 at 1–2
days effort, not Tier 2.  
**Effort:** 1–2 days (revised down from 3).

---

### 9. `assert` with message → `check` with Why3 label

Extension of item 1. When `assert cond, msg` is written, the message string surfaces as
a Why3 `[@expl:<msg>]` label on the check goal, making proof failure messages
human-readable in the Why3 IDE.  
**WhyML output:** `check { [@expl:<msg>] cond }`  
**Effort:** +1 day on top of item 1.

---

## Tier 3 — High cost (future work)

### 10. `match` statement (Python 3.10+)

**Gap:** `ast.Match` is completely absent.  
**Value:** Pattern matching is increasingly common in modern Python. In WhyML, `match`
maps to `match ... with | Pattern -> ... end`.  
**Difficulty:** A minimal implementation covering literal and capture patterns takes 2–3
weeks; full pattern support (mapping, sequence, class patterns) is a multi-month project.  
**Deferred until:** After Tier 1 and Tier 2 are complete.

---

### 11. Lambda functions

**Gap:** `ast.Lambda` returns `UnknownPyExpr`.  
**Value:** Higher-order functions (`sorted(arr, key=lambda x: -x)`) appear in many Python
programs. Requires function types in the IR and `fun x -> e` emission in WhyML.  
**Difficulty:** Closures over mutable state are particularly hard to formalize.  
**Deferred until:** After the formal semantics in `form/` is complete.

---

## Out of scope (fundamentally incompatible with Why3)

### 12. Generator expressions and `yield` — not recommended

**Gap:** `ast.GeneratorExp`, `ast.Yield`, `ast.YieldFrom` are unsupported.  
**Recommendation:** Do not pursue. Lazy semantics do not map cleanly to Why3's eager
evaluation model. Abstract generator calls via `\trusted` stubs in `data/lib_stubs/`
(e.g., stub `itertools.chain` as returning a list with known bounds).

---

### 13. Async / await — not recommended

**Gap:** `ast.AsyncFunctionDef`, `ast.AsyncFor`, `ast.AsyncWith`, `ast.Await`.  
**Recommendation:** Do not pursue. Async semantics requires a concurrency model that
Why3 does not natively support.

---

## Implementation order summary

| # | Extension | Effort | Modules touched | Notes (2026-05-18) |
|---|---|---|---|---|
| 1 | `assert` → `check` | 1–2 d | M5, M6 | |
| 2 | `//` and `%` in contracts | 1 d | M2 | |
| 3 | `True`/`False`/`None` in contracts | 1 d | M2, M5, M6 | |
| 4 | `in` / `not in` in contracts | **1 d** | **M2 only** | M5+M6 body support exists |
| 5 | Missing library stubs | 1–2 d each | `data/lib_stubs/` | Only `functools`, `itertools` remain |
| 6 | Walrus operator `:=` | 3 d | M5 | |
| 7 | Slice notation | 1 wk | M2, M5, M6 | |
| 8 | Tuple unpacking | **1–2 d** | M5, M6 | Simpler than estimated; could be Tier 1 |
| 9 | `assert` with Why3 label | +1 d | M5, M6 | Merge with item 1 |
| 10 | `match` statement | 2–3 wk | M2, M3, M5, M6 | |
| 11 | Lambda functions | deferred | M4, M5, M6 | |
| 12 | Generators / yield | **never** | — | Out of scope |
| 13 | Async / await | **never** | — | Out of scope |

## Key files for implementation

- `src/pycsl/Module2_Parser.py` — EBNF grammar (items 2, 3, 4, 7)
- `src/pycsl/Module3_Weaver.py` — AST annotation attachment (item 10)
- `src/pycsl/Module5_IREmitter.py` — Python AST → IR (items 1, 3, 4, 6, 7, 8)
- `src/pycsl/Module6_WhyMLTranspiler.py` — IR → WhyML (items 1, 3, 4, 7, 8)
- `data/lib_stubs/` — trusted library contracts (item 5)
- `test-suite/corpus/pycsl-reference/` — reference tests for each new feature
- `test-suite/annotations.md` — document each new annotation (NEVER renumber existing entries)
