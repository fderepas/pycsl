# Plan: no-more-int Part 4 — the residual tail after `no-more-int-3.md`

Standalone successor to `no-more-int-3.md`. Part 3 closed the high-value real-type tracks and the
emitter refactor; what is left is a **demand-driven backlog** — each item is gated on a concrete
driver (the Gate-A discipline) and several are explicitly *default-don't-build*. Nothing here is on
a critical path; this file exists so the residue is recorded, not lost.

## Where we are after `no-more-int-3.md` (all committed + pushed)

| Landed in Part 3 | What it bought |
|---|---|
| **Track 2a** sum types + `match`/`case` (0520/0521) | `#@ datatype`, variant `type_decl`, exhaustiveness via Why3 |
| **A1 T1.1** dict **string values** (ν) | `Dict[int, str]` carries content through a dict (0523) |
| **A1 T1.2** dict **string keys** (κ) | distinct runtime string keys provably non-aliasing (0526) |
| **Faithful KeyError** (opt-in `#@ no_exception KeyError`) | `d[k]` missing → proof obligation, not a silent default (0524/0525) |
| **A2a** method calls on a record **param** (0522) | `a.bump(k)` propagates the callee's result/param `ensures` |
| **A2c** field-referencing method `ensures` (0529) | `b.get_x()` propagates `\result == self.x` via a receiver param — unblocks StringIO/NodeVisitor getter stubs |
| **A5a** recursive datatypes, single self-recursive (0527/0528) | `type tree = Leaf \| Node tree tree` + `\variant` termination |
| **Part B** emitter refactor, moves 1, 2, 3a–3e | type-dispatch unified, pre-decl exclusion consolidated, the giants split into `module5/` + `module6_whyml/` mixins — all byte-identical |

The **int collapse** is now ~deliberate-tractability only: strings, floats, records, variants, and
dict key/value types are all real where a driver demanded them. The remaining collapses are either
*hard* (need frame machinery / a string parser), *low-value* (itertools), or *benign* (bool, bare
tuple). Each below states its **gate**, **risk**, and a **verdict**.

---

# PART A — remaining real-type tracks (all gated on a demand-driver)

## A2b — record-param **mutation** (`p.f = v` written back to the caller)  — HARD, deferred
Why3 records are by-value, so a method/function that assigns `self.f`/`p.f` does **not** propagate
the write to the caller's instance. Faithful support needs `ref`-passing with a `writes p.f` frame
obligation (or a documented value-semantics boundary the user accepts).
- **Gate / driver:** a function mutates a passed object and the caller observes the write
  (`def set(p, v): p.f = v` then `p.f == v` caller-side).
- **Risk:** medium-high (frame machinery touches the whole call-lowering + aliasing story).
- **Verdict:** **defer** until a real driver demands it; until then record params stay read-only
  (A2a/Track 3 scope). The honest alternative if no driver appears: keep the value-semantics
  boundary documented in the annotate SKILL.

## A3 — bounded eager `itertools`  [Backlog G] — NOT STARTED, low value
Bounded-array under-approximation of the **eager** subset (`chain`/`islice`/`product`/
`combinations`). Lazy/infinite (`cycle`/`count`/`repeat`, `yield`) stays **out of scope** — no
SMT-tractable stream model.
- **Gate / driver:** `len(chain(a, n, b, m)) == n + m` + an element-membership contract.
- **Risk:** low and self-contained (new abstract ops + a length model; no core-path change).
- **Verdict:** **build only on a concrete bounded-itertools driver.** Low value; independent.

## A4 — `json` round-trip (`loads(dumps(x)) == x`)  [Backlog C tail] — SHELVED (string-parsing wall)
The sum-type/recursive-type *infrastructure* exists (Track 2a + A5a), so the only missing json
piece is the **round-trip**, which needs string → value parsing and value → string serialization —
the niche, hard part the spike explicitly did not establish.
- **Dependencies:** a recursive `#@ datatype Json = …` (needs A5a — done for single self-recursion;
  `JObj` additionally needs A1's `map string json`, i.e. a **nested-map value type**, see A1-residual
  below), plus a bounded-depth round-trip contract likely citing a Rocq/Lean lemma (the `0342` gcd
  template — SMT over a recursive union + maps is heavy).
- **Verdict:** **default: don't build** absent a compelling json-content driver. If pulled, it is a
  multi-step effort (recursive datatype + string parser + bounded lemma), not a one-sitter.

## A1-residual — dict value/key types **beyond `int`/`string`**  — partial
T1.1/T1.2 threaded ν, κ ∈ {`int`, `string`}. The full Backlog-A/B target is ν ∈ {`int`, `string`,
`array int`, **nested map**} and κ likewise. So **dict-of-lists** (`Dict[str, List[int]]`) and
**dict-of-dicts** (`Dict[str, Dict[...]]`) still collapse the value to `int`.
- **Gate / driver:** `Dict[str, List[int]]` with `d[k] = xs` then `len(d[k]) == len(xs)` (array
  value carries content); then `Dict[str, Dict[int,int]]` (nested map) — the `JObj` enabler for A4.
- **Risk:** medium — the ν side-map and the `None -> <default ν>` arm already exist (T1.1); this
  extends ν's domain to `array int` / `map …` and the default to `(Array.make 0 0)` / `(const None)`.
  Blast radius is the dict path; **full dict-corpus sweep is the gate** (not byte-diff).
- **Verdict:** **highest practical value of the residual tracks** (composes the string + list + dict
  models, and is the precondition for A4's `JObj`). First to take if any nested-container driver
  appears.

## A5b/A5c/A5d — sum-type extensions (follow-ons to A5a)  — build on demand
- **A5b — captures referenced in contracts.** A `case`-bound capture is in scope only inside its
  arm, not at `requires`/`ensures` level. Surfacing per-arm postconditions (or a `\match`-style spec
  operator) is a real extension. *Gated on a driver needing a per-arm postcondition.*
- **A5c — guarded / nested / or-patterns** (`case Some(n) if n > 0`, nested ctors, `A | B`). The
  pure_ast pattern parser + match lowering handle only **flat single-level** constructor patterns.
  Each shape is a parser + lowering extension. *Build per shape on demand.*
- **A5d — parametric datatypes** (`Option[T]`): a generic variant over a type param; composes with
  A1's parametric machinery. *Low priority.*
- **A5a-residual — mutually-recursive datatypes** (`type a = … with b = …`). A5a did single
  self-recursion; mutual recursion needs the `with` form in `preamble.py::_emit_type_decls`. *Gated
  on a mutually-recursive-datatype driver (e.g. an AST with `Expr`/`Stmt` referring to each other).*

## A6 — retire `_coerce_to_int` categories (cross-cutting hygiene)  — partially actionable NOW
`_coerce_to_int` (`expressions.py`, ~line 119) erases real types (string→hash, array→0, map→0,
tuple→hash, self→abstract-op). The discipline: **as each track lands, remove that track's coercion
category** rather than leaving dead erasure. End state: it fires only for genuinely-untyped (`Any`)
operands.
- **Actionable now (no new feature needed), each its own commit + full sweep:**
  - **Audit the record/self→int category is actually gone** post-A2a/A2c (Track 3 was supposed to
    remove it for record params).
  - **Remove the dict key/value→int erasure** now that A1 T1.1/T1.2 thread real ν/κ — any residual
    `_coerce_to_int(v)`/`_coerce_to_int(k)` on a typed dict path is now dead for ν/κ = string.
- **Risk:** medium — `_coerce_to_int` is load-bearing; removing a category can surface a path that
  *relied* on the erasure. **Gate:** full sweep, zero pass/fail delta; do **one category per commit**
  with a driver that exercises the now-typed path. Never fold into a feature commit.
- **Verdict:** **the cleanest standalone next step** — it is debt paydown gated only by the sweep,
  needs no demand-driver, and shrinks the collapse surface measurably.

## A7 — residual benign collapses — DOCUMENT ONLY, do not build
`bool` as `1/0` and bare `tuple → int` (hash) are rare and benign. **No driver should chase these.**
Keep them documented in the τ-table (annotate SKILL / static-semantics reference). Action item is
only: ensure the τ-table still lists them as *intentional* after the Part-B anchor refresh.

---

# PART B-tail — emitter-refactor remainder (moves 4–5)

Moves 1, 2, 3a–3e landed byte-identical. Two moves remain, both pure hygiene (no behavior change):

- **Move 4 — kill dead erasure as types land** (this *is* A6 above, viewed from the refactor side):
  remove `_coerce_to_int` categories already superseded by a landed track. Same gate as A6.
- **Move 5 — mechanical hygiene:** dead-code / unused-import sweep across the now-split
  `module5/` + `module6_whyml/` packages; **re-point the `file:line` anchors** the no-more-int work
  cites in the skills/docs (they drift after the move-3 extraction — `bin/doc-coherency.py --check`
  + grep the SKILLs for stale `expressions.py:NNN` / `statements.py:NNN` / `Module5_IREmitter.py:NNN`
  citations); consistent naming for the new type-kind vocabulary introduced in move 1.
- **Gate (every move):** full corpus sweep zero delta; byte-diff `.mlw` for a representative sample
  where the change is purely structural; `bin/doc-coherency.py --check` green; one concern per
  commit; **no** behavior change folded in. Also confirm whether `src/self-annotate/src/` (the
  mirror) must track the change (`bin/check-self-annotate-sync.sh`).

---

## Suggested order (what to pull next, by leverage)

1. **A6 / Part-B move 4 — retire superseded `_coerce_to_int` categories.** No driver needed, gated
   only by the sweep, shrinks the collapse surface. Start with the dict key/value→int category (now
   dead for typed dicts post-T1.1/T1.2) and the record/self→int audit. **Highest-leverage, lowest-
   risk, available today.**
2. **Part-B move 5 — mechanical hygiene + anchor refresh.** Cheap, keeps the docs/skills honest
   after the move-3 split.
3. **A1-residual — nested-container dict values** (`Dict[str, List[int]]`, then nested maps) — *if* a
   container-of-container driver appears. Highest feature value; also unlocks A4's `JObj`.
4. **A5b/A5c/A5d, A5a-residual, A2b, A3** — each strictly on its own demand-driver; otherwise leave.
5. **A4 (json), A7** — default don't-build / document-only.

## Critical files (refresh anchors per Part-B move 5)
`src/pycsl/module6_whyml/functions.py` (the three method-ensures maps: `_build_method_result_ensures_map`
/ `_build_method_param_result_ensures_map` / `_build_method_field_result_ensures_map`) ·
`expressions.py` (`_coerce_to_int` ~119, `_resolve_dotted_signature`/`_handle_dotted_call`,
dict MapGet/MapSet) · `statements.py` (`map_update_some`, dict-set ν/κ coercion) ·
`module6_whyml/preamble.py` (`_emit_type_decls` — variant payload resolution, the A5a/A5a-residual
site) · `Module5_IREmitter.py` + `module5/` package · `Module4_SemanticAnalyzer.py`
(`dict_value_types`/`dict_key_types` capture). Line numbers drift after Part-B move 3 — re-derive by
symbol, not by the citations above.
