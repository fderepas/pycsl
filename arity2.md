# arity2.md — finish the inliner array fix (layer 2b) and **gate it**

**Status:** Plan / not started
**Supersedes the open half of:** `arity.md` (layer 2a landed as `35441ec`; 2b still open)
**Review that motivated this:** `comment.md`
**Source of truth:** `src/pycsl/ir_inline.py`, `src/pycsl/module6_whyml/{types,statements}.py`,
`inline.md` (Phases 1–3)

---

## 0. Where we are (committed state)

- `35441ec` landed **layer 2a only** (declaration typing): inlined array temps now get a
  typed declaration via post-hoc inference (`_collect_array_var_assigns` + transitive
  fixpoint + `seed`; `_field_type_of` resolves `global.<field>`; dotted-receiver freshening).
- **Layer 2b is open:** the per-operation-site `is_array` decision
  (`statements.py:388-405`) does **not** see those inlined temps, so an array *mutation*
  `a[i] = v` inside an inlined body still emits the abstract
  `subscript_set (x:int)(i:int)(v:int)` (`statements.py:459`) instead of the concrete
  `a[i] <- v` + `Array.length` bounds check (`statements.py:413`). → Why3 type error.
- **The fix is ungated:** no `test-suite/corpus/pycsl-reference` driver exists for it, and
  there is no byte-diff evidence. A refactor can silently regress 2a *and* whatever 2b adds.
- `8d9f749` worked around all this by deforming `pure_lib/os` (vacuous `ensures True`,
  `-> bytes` bodies relabelled `-> list`, `scandir` yielding ints not `DirEntry`). Those are
  faithfulness debt to unwind once the transpiler gaps close (Phase 4).

**This plan's two jobs:** (1) fix 2b in the transpiler; (2) put a permanent gate around the
whole inliner-array feature so it can't silently rot. Gating is Phase 1 — *before* the fix.

---

## Phase 1 — GATE FIRST (reference-corpus drivers + byte-diff)

Per the demand-driven / reference-corpus discipline (`pycsl-how-to-develop`), the gate is
authored before the fix and starts RED.

### 1a. Reference-corpus drivers (`test-suite/corpus/pycsl-reference/`)

Mirror the inline-family convention of `0576`–`0582` (docstring states the Phase;
`# pycsl-flags: --memory-model hoare`; `# pycsl-expected: FAIL` on negatives):

- **`0583` (positive, 2a):** imported-class module global; method takes an `array int`
  param; inlined call **reads** an element; prove a true postcondition. (Locks in `35441ec`.)
- **`0584` (positive, 2a):** method **returns** `array int`, inlined in **expression
  position** (exercises `_hoist_calls_in_expr` + `_inl_res` + the transitive `inode := !_inl_res`
  chain). Prove a fact about the result.
- **`0585` (positive, 2b — the new fix):** inlined body **mutates** the array (`a[i] = v`);
  prove a postcondition about the mutated element. **This is the driver that must flip from
  FAIL→PASS when Phase 2 lands.** Start it as a plain test that currently fails.
- **`0586` (negative, `# pycsl-expected: FAIL`):** false post-claim about the mutated/returned
  array — confirms the inlined array path is not vacuously typed/true.

These run automatically under `bin/run-reference-tests.sh --pycsl` (no harness change needed
— the suite globs the directory). Record expected outcomes so `0585` reads PASS only after
Phase 2.

### 1b. Emission-identical byte-diff gate

`35441ec` and Phase 2 touch `types.py`/`statements.py`, which type **every** function. Run
`bin/extraction-byte-diff*.sh` to prove a driver that does NOT trigger array-temp inlining
emits **byte-identical** WhyML before/after. The typing changes must be inert on the
non-array path. Capture this as part of the gate, not a one-off.

### 1c. Exit criterion for Phase 1

`0583`/`0584` PASS (2a already landed), `0585` FAILs with the `subscript_set … expected int`
error (proving the gate detects the open bug), `0586` XFAILs, byte-diff clean.

---

## Phase 2 — fix layer 2b (operation selection)

**Root cause:** declaration-typing and operation-selection read **different** array sets.
Declaration uses `_typed_local_vars` (= `find_array_and_dict_vars` ∪
`_collect_array_var_assigns`, `statements.py:824-837`). Operation selection at the subscript
site reads `_array_locals` + an inline `FieldGet` check (`statements.py:388-405`). Inlined
temps reach the first set but not the second.

**Fix (unify the source of truth):** make the authoritative array-local set computed for
declaration also populate `_array_locals` (or have the `is_array` decision at
`statements.py:388` consult `_typed_local_vars`' result directly). One set drives both
declaration and every operation site. Then `a[i] = v` on an inlined temp takes the concrete
`is_array` branch (`statements.py:413`) → `a[i] <- v` with the `Array.length` bounds assert,
no `subscript_set`.

**Also cover the read/other-op sites**, not just subscript-set: audit every place that
branches on `_array_locals` (`statements.py:122,536`; `stmt_control_flow.py:104`;
`expressions.py:541-573`) to confirm an inlined array temp is now handled uniformly
(subscript read, slice, `len`, iteration).

**Design note (debt):** §2c of `arity.md` stands — there are ≥5 overlapping array detectors.
Unifying them fully is out of scope here, but Phase 2 should *reduce*, not grow, the count:
prefer routing the operation site to the existing `_typed_local_vars` result over adding a
sixth detector. If a clean single-set refactor is feasible, do it; otherwise leave a
`# TODO(arity): unify array-local detection` and a one-line note here.

**Exit:** `0585` flips FAIL→PASS; `0583`/`0584`/`0586` unchanged; byte-diff still clean.

---

## Phase 3 — close the smaller transpiler gaps the workarounds exposed

Each gap currently forces a source deformation in `pure_lib/os`. Fix the gap, add a corpus
driver, then Phase 4 can unwind the deformation.

- **3a. `bytes`/`list` unification.** `-> bytes` is not treated as `array int`, which is the
  *root* of the "relabel `-> bytes` as `-> list`" hack (`comment.md` #1). Make a
  `bytes`-returning/typed function lower to `array int`. Driver: a `_pack_*`-shaped function
  returning `bytes`, inlined, element read. (Highest leverage — removes the temptation to
  mislabel return types.)
- **3b. Tuples-in-arrays.** `_unpack_direntry -> tuple` and `_read_directory` returning a
  list of tuples forced the `listdir`/`scandir` consumer rewrites (`comment.md` #5).
  Scope/lower or explicitly document-and-reject; add a driver either way.
- **3c. Bitwise `~`.** `_set_bitmap` was rewritten to avoid `~` (`comment.md` #4). Add `~`
  support (or document the rejection); driver exercising `x & ~mask`.

If any gap is genuinely deferred, `log()`/document it as an explicit limitation rather than
leaving the workaround to read as "supported."

---

## Phase 4 — unwind the `pure_lib/os` faithfulness deformations

**Depends on Phases 2–3.** Only after the enabling gaps close:

- Restore `_pack_* -> bytes` (real return type; body already returns `bytes`).
- Restore real postconditions where `ensures True` was substituted (e.g. `\result >= 0`,
  length facts). Anything that still can't be proven becomes a tracked `# TODO(arity)`, not a
  silent `True`.
- Restore faithful `os` semantics: `scandir` yields `DirEntry` objects (not inode ints);
  `DirEntry.path` keeps its leading-`/`; `listdir`/`scandir` go back through
  `_read_directory` once tuples-in-arrays (3b) works.
- **Re-run `report.md`** for an HONEST assurance number, and append the byte-diff result. The
  current 93.4 % is partly vacuous contracts — the restored number is the real one, even if
  lower.

---

## Phase 5 — commit hygiene

- Split the ~35 k-line vendored CPython `lib/` tree out of the `8d9f749` "Fix os module"
  history (separate vendoring commit, or `.gitignore`). Not blocking, but do before it
  ossifies.

---

## Sequencing & landing

1. Phase 1 (gate, RED) — commit the drivers + byte-diff harness wiring.
2. Phase 2 (2b fix) — `0585` flips to GREEN in the same commit as the fix.
3. Phase 3 (gaps) — one commit per gap, each with its driver.
4. Phase 4 (unwind deformations + honest `report.md`) — one commit, gated by 2/3.
5. Phase 5 (hygiene) — independent.

**Every code commit must show:** full `bin/run-reference-tests.sh` green (PASS/XFAIL), the
relevant `058x` driver(s) in the diff, and a clean byte-diff. No transpiler change lands
without a corpus driver — that is the gate this plan exists to install.

---

## Out of scope

- Strategy A (assert-at-inline-boundary) re-architecture — `35441ec` committed Strategy B;
  this plan finishes B and gates it rather than re-cutting. Revisit only if 2b can't be made
  clean within B.
- Recursive-method inlining (refused — `0580`); global aliasing (banned — `ir_inline.py:308`).
- 2-D (`matrix`) inlined temps — extend only on demand.
- **Do NOT** add further `pure_lib/os` deformations to chase the number; fix the transpiler.
