# Plan: the residual "everything-is-int" model — do-now vs gated-backlog

## Context & verdict

PyCSL collapses most Python types onto Why3 `int`. This session promoted `str` to real
`string.String`; many collapses remain. A pros/cons weighing concluded that **the int-collapse is
~20% genuine debt and ~80% a deliberate, load-bearing simplification**: "everything is int" is
*why* PyCSL's SMT goals discharge in ~0.01s. So "remove the int model" is the wrong goal.

The right goal is: **fix the one unsound collapse, add the high-ROI referential-transparency
capability now, and expand real types elsewhere only where a concrete driver demands it** (the
project's Gate-A discipline). This file is split accordingly.

### Inventory (reference)

| Collapse | Today | Real target | Where it belongs |
|---|---|---|---|
| **float** | `int` (no theory) — **UNSOUND** | `real.Real` + bridges | **Do now (D)** |
| **referential transparency / lru_cache** | `pure`/`assigns \nothing` exist; RT not exposed | RT predicate + `let function` + lru_cache rule | **Do now (F)** |
| dict/set **value** | `map int (option int)` (value int) | `map κ (option ν)` | Backlog A (gated) |
| dict/set **key** | int (string keys hashed) | `map string …` | Backlog B (gated) |
| bare class **param** | `int` + opaque `getattr_<cls>` | reconstruct `record c` | Backlog E (gated) |
| **sum/recursive types** (json) | only `record` + `option int` | `type t = A \| B x \| …` + match | Backlog C (shelved) |
| **iterators / `yield`** (itertools) | none (arrays only) | lazy model / bounded under-approx | Backlog G (shelved) |
| bool `1/0`, bare tuple→int | — | benign / rare | leave; document |

Anchors: `functions.py:26-36`/`522-532` (type collapses), `preamble.py:584-595` (fields),
`expressions.py:119-148` (`_coerce_to_int`), `:1118-1125` (MapGet), `statements.py:751-769`
(map value `int`); `Module5._mark_pure:1440`; `functions.py:283-294` (`can_emit_as_logic`).

---

# PART 1 — DO NOW

Two self-contained pieces: a soundness fix and a high-value capability. Each gated by the full
corpus sweep (zero new regressions) before commit.

## Stage D — `float` → `real.Real` (soundness fix)

`τ(float)=int` lets int arithmetic stand in for float arithmetic — it can prove false goals. Fix:

- `use real.Real`; τ(float) = `real`; float literals → real constants; float ops bridge through
  abstract `val float_add_op (a b: real): real` … (the val-bridge pattern from strings).
- Detect float-typed params/locals/returns in `functions.py` type emission (mirror the `str`→
  `string` branch) and route float ops in `_handle_binop`.
- **Migration:** the differential enumerates every float-using file; each must re-prove or be
  re-marked (some "proofs" relied on the unsound int-float behaviour — those *should* now fail).
- *Driver:* a float contract that proves under `real`; a negative that the old unsound int-float
  identity no longer holds.
- *Boundary:* transcendentals (sin/cos/exp…) stay opaque abstract ops over `real` (no closed form).

## Stage F — referential transparency + sound `lru_cache` — ✅ DONE

**Status (implemented):** `Module5._is_memoized` flags `@lru_cache`/`@cache`/`@cached_property`;
`_check_memoization_soundness` rejects (UB-7.7) unless the function is referentially transparent —
pure (`_detect_purity`: `assigns \nothing`, no `\trusted`/`\diverges`) AND reads no `#@ shared`
mutable global (`_reads_any`). RT is *inferred* (no new annotation needed); a pure non-method
function is already emitted as a Why3 `let function` (RT by construction), so the cache is
observationally transparent and no extra emission is required — only the gate on the unsound case.
Drivers `0515` (pure `@lru_cache` + caller proof), `0516` (non-RT rejected); UB catalog §7.7.
Contracts must be placed ABOVE the decorator to attach. *(T-RT2's explicit `#@ deterministic`
annotation was not needed and is deferred — RT is inferred.)*



**Why high-ROI:** Why3 `let function` symbols are referentially transparent *by construction*, and
PyCSL already emits `pure`+no-locals+non-method functions that way (`functions.py:283`,
`_mark_pure:1440`). The work is to make the property explicit, checkable, and usable at a memoizing
call site — no higher-order modeling needed.

A function is **referentially transparent (RT)** iff: (a) `#@ assigns \nothing` (effect-free —
exists), (b) it reads no mutable / `#@ shared` module global (new), (c) it calls only RT functions
(new), (d) it is not `\trusted`/`\abstract` (new), (e) not `diverges` (exists).

Task list:

- **T-RT1 — define the RT predicate** combining (a)–(e). (a),(e) exist; (b),(c),(d) are new.
- **T-RT2 — surface `#@ deterministic`** (a user RT assertion) parsed in Module2, validated in
  Module4 against T-RT1 (hard error if violated). RT may also be *inferred* when T-RT1 holds.
- **T-RT3 — emit RT functions as Why3 `let function`** (extend `can_emit_as_logic`,
  `functions.py:283`): a `let function f` gives `forall x. f x = f x` for free — the determinism
  axiom — with no separately-emitted lemma.
- **T-RT4 — no-global-read scan** (new IRScanner pass): a body reading a `#@ shared`/mutable global
  is not RT; module *constants* are fine. Feeds T-RT1(b).
- **T-RT5 — model `lru_cache`/`cache`/`cached_property` soundly**: require the wrapped function to
  be RT; under that, `lru_cache(f)(x) == f(x)` (the cache is observationally transparent), so the
  decorated function keeps its own contract. If the wrapped function is **not** RT → **reject**
  (new UB: "memoizing a non-deterministic / effectful function is unsound"), mirroring UB-7.5/7.6.
  Recognition is *syntactic* (the decorator) — no first-class function values.
- **T-RT6 — corpus drivers**: positive (an RT `@lru_cache`d function; caller proves the same
  postcondition as undecorated); negative `# pycsl-expected: FAIL` (memoizing a global-reading or
  state-assigning function → rejected).
- **T-RT7 — docs**: an RT subsection in static-semantics (predicate + lru_cache rule) and the UB
  catalog (reject-impure-memoization).

## Do-now verification

Per stage: flagship driver proves; full corpus sweep (`PYTHONHASHSEED=0`, honor `# pycsl-flags:`/
`# pycsl-expected:`, diff vs the committed baseline) — zero new regressions; τ-table update for
float (static-semantics §1.4 + translational §T.2.2) and `doc-coherency.py --check` green.
Float is a core-emitter change (watch the blast radius); RT is additive (low risk).

---

# PART 2 — GATED BACKLOG

Do **not** start any of these without (1) a named demand-driver — a real verification-grade
program that **fails today** because of the collapse — and (2) for the recursive/lazy ones, a
Stage-0 SMT-feasibility spike. Core-path changes carry a full-corpus blast radius.

## A — parametric dict/set **value** type  *(gate: a driver needing non-int dict values)*
Let the dict VALUE be a real type (start `string`, then arrays/maps). Drop the
`map_update_some … (v: int)` hardwire (`statements.py:759`); value type flows from the parsed
`Dict[K, V]` element types (currently discarded); stop `_coerce_to_int` on known-typed values.
Medium value, **high risk** (core dict path touched by much of the corpus).

## B — string-keyed dict  *(gate: a driver with `d["key"]` content reasoning)*
KEY type `string` (`map string …`); stop hashing string keys (`_coerce_to_int:122`). Low–medium
value, medium risk. Likely paired with A.

## E — reconstruct bare class **params** as records  *(gate: an object-passing API that needs field reads)*
Type a `C`-typed param as `record c` (drop the coarsen-to-int path, `functions.py:36`), so field
access is direct instead of opaque `getattr_<cls>`/`self_to_int_<cls>`. Medium value, medium risk.

## C — sum/recursive types + json  *(SHELVED: needs a driver AND an SMT spike)*
A whole new capability: emit Why3 `type json = JNull | JBool bool | JInt int | JStr string | JArr
(list json) | JObj (map string json)`, plus pattern matching in Module5 IR + Module6. **Low
practical value** (json is niche for an integer-domain verifier), **very high cost**, and the
round-trip `loads(dumps(x))==x` "may need a cited Rocq/Lean lemma" — SMT over a recursive union +
maps is heavy. Probe feasibility (a strings-plan-Gate-B-style spike) before committing; default to
*not building* absent a compelling driver.

## G — iterators / itertools  *(SHELVED: partly infeasible)*
No iterator/lazy model exists. Lazy/infinite generators (cycle/count/repeat) are **not
SMT-modelable**; at most a bounded-array under-approximation for the eager subset
(chain/islice/product/combinations). Low value, high cost. Build only the bounded subset, only on
demand, and document the lazy boundary.

## Backlog discipline
Each item, when triggered: commit the failing demand-driver as `# pycsl-expected: FAIL` first;
implement; flip it; full-sweep gate; τ-table + doc-coherency. Stop at the YAGNI exit if the driver
turns out not to need it.

---

## Critical files (both parts)

- `src/pycsl/module6_whyml/functions.py` — type→WhyML collapses (`_param_type_str`/
  `_symtype_to_whyml`/`_compute_return_type` ~26-36/522-532); `can_emit_as_logic` (RT, ~283).
- `src/pycsl/module6_whyml/expressions.py` — `_coerce_to_int` (~119-148); MapGet (~1118-1125);
  `_handle_binop` (float ops, str-bridge pattern).
- `src/pycsl/module6_whyml/statements.py` — `map_update_some` value type (~751-769).
- `src/pycsl/module6_whyml/preamble.py` — field types (~584-595); + algebraic `type` emission (C).
- `src/pycsl/Module5_IREmitter.py` — `_mark_pure` (~1440); no-global-read RT scan (T-RT4);
  `Dict[K,V]` element-type capture (A/B); pattern-match IR (C).
- `src/pycsl/Module2_Parser.py` / `Module4_SemanticAnalyzer.py` — `#@ deterministic` (T-RT2);
  tagged-union surface (C).
- docs: static-semantics §1.4 (τ float reversal + RT predicate), translational §T.2.2/§T.6, UB
  catalog (reject-impure-memoization); `test-suite/corpus/pycsl-reference/` drivers per stage.
