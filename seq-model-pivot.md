# seq-model-pivot.md — model reassignable list locals as immutable `seq` (the 12th handler)

**Doctrine:** [no-more-int] — model a Python list faithfully. A Python list is a **value**
(reassignable, sliceable) — Why3's mutable `array` (region-typed, non-reassignable-across-
regions) is the wrong model for a local that is REASSIGNED. This plan models a reassignable
list-elem local as an immutable Why3 **`seq`**, closing the last `\trusted` handler
`_handle_critical_section_stmt` (→ **12/12**).

**Sub-plan of** `self-ir-schema.md` §8 (IR5). The `self.ir` reflection (IR1–IR4) is DONE; the
only remaining blocker is `body_stmts = body_stmts[:-1]` reassigning a `ref (array emit_ir)`,
which Why3's region system rejects (*"illegal alias"*).

**Feature-vs-refactor:** FEATURE, **byte-clean by construction** — every change is gated on
`@mutable_state` and the element-type map (empty for the 627-corpus). Gate: **byte-diff 0** +
type-check + a checked frame + non-vacuity.

---

## 0. The verdict — exactly why `array` fails and `seq` works

```python
body_stmts = stmt.body            # array emit_ir field  → snapshot to `seq emit_ir`
body_stmts[-1]                    # Seq.get body (Seq.length body - 1)
body_stmts = body_stmts[:-1]      # ← REASSIGN. `ref (array _)` reassignment = illegal alias.
                                  #   `seq` is a pure value → `body := body[0 .. len-1]` is fine.
[s.to_dict() for s in body_stmts] # comprehension over a `seq` → list_comp_seq_<τ>
```

**Why3 fact.** A `ref (array 'a)` cannot be reassigned to a fresh-region array (`Array.sub`
returns a new region) — the region system forbids it. A `seq 'a` is a **pure immutable value**
(like `int`): `ref (seq 'a)` is freely reassignable (`body := <any seq>`), sliceable
(`body[i..j]`), indexable (`Seq.get`), with no regions. The codebase ALREADY models growable
(`.append`) lists this way (`07-1705`: `_seq_locals`, `snapshot : array int → seq int`,
`Seq.cons`/`Seq.snoc`/`Seq.get`/`Seq.length`). This plan **reuses that machinery**, generalised
to (a) `emit_ir`/`string` element seqs and (b) REASSIGNED (not only `.append`-grown) locals.

---

## 1. The model

- A list-elem local that is **reassigned** (`x = x[:-1]`, `x = <other list>`) OR grown
  (`.append`) is a `ref (seq <elem>)` — `<elem>` ∈ {`int`, `string`, `emit_ir`} from
  `_array_elem_types` / `_seq_value_types`.
- **Bridge from an array** (a `List[τ]` field read, `body_stmts = stmt.body`): `snapshot`
  generalised to `array 'a → seq 'a` (polymorphic; the existing `array int → seq int` is the
  int instance).
- **Slice** `x[:-1]` → `x[0 .. Seq.length x - 1]` (Why3 `seq` sub-sequence).
- **Index** `x[-1]` → `Seq.get x (Seq.length x - 1)`; `x[i]` → `Seq.get x i`.
- **Comprehension** `[f(s) for s in x]` over a `seq` → `list_comp_seq_<τ> (src: seq 'a) : seq <τ>`
  (the seq analogue of L1's `list_comp_<τ>`), with the same length law.
- **for-loop / len / truthiness** over a seq → `Seq.length` / `Seq.get` (already handled for
  `_seq_locals`).

**Sound:** `seq` is a faithful value model of a Python list (immutable snapshot semantics for
these read-only-then-reassign uses); content stays opaque where the source op is opaque
(`snapshot`, `list_comp_seq`). `ensures True` + frame only.

---

## 2. Stages (byte-diff-gated)

- **SQ1 — promote reassigned list-elem locals to `_seq_locals`.** A local in `_array_elem_types`
  that is REASSIGNED (a later `x = …` after the first bind) joins `_seq_locals` with its element
  value type (`_seq_value_types[x] = elem`). *Gate:* `body_stmts` is a `ref (seq emit_ir)`.
- **SQ2 — polymorphic `snapshot` + field-read bridge.** `snapshot : array 'a → seq 'a`; a
  `List[τ]` field read bound to a seq local is `snapshot`-bridged. Generalise `_seq_init_expr`
  to a non-int element (`Seq.cons` chain for a literal; `snapshot` for an array-valued RHS).
  *Gate:* `body_stmts = stmt.body` → `ref (snapshot stmt.body)`.
- **SQ3 — seq slice / index.** `x[:-1]` → the seq sub-sequence; `x[-1]`/`x[i]` → `Seq.get`.
  Route through the existing `_seq_locals` subscript path, extended to negative/last and slice.
  *Gate:* `body_stmts = body_stmts[:-1]` and `body_stmts[-1]` type-check (no alias).
- **SQ4 — seq comprehension.** `[f(s) for s in <seq>]` → `list_comp_seq_<τ>` (the L1 dispatch
  chooses the seq variant when the iterable is a seq). *Gate:* `[s.to_dict() for s in
  body_stmts] : seq emit_ir`.
- **SQ5 — un-`\trust` `_handle_critical_section_stmt`** with `assigns self._havoc_counter` (the
  only transpiler-state write) + any loop invariant the `for var in shared_for_mutex` read
  needs. *Gate:* verifies un-`\trusted`; suite green; byte-diff 0.

SQ1 gates SQ2–SQ4; SQ5 needs all.

---

## 3. Critical files

- `src/pycsl/module6_whyml/statements.py` — `_seq_init_expr` (non-int element + array bridge),
  `_typed_local_vars` (promote reassigned list-elem locals to `_seq_locals`), `_handle_seq_assign`.
- `src/pycsl/module6_whyml/expressions.py` — the `snapshot` decl (polymorphic), `_handle_subscript`
  (seq slice + `Seq.get` for a seq local incl. negative index), the L1 `ListComp` dispatch
  (seq-iterable → `list_comp_seq_<τ>`), the `.join` seq path (already present).
- `src/pycsl/module6_whyml/stmt_control_flow.py` — for-loop over a seq (already `Seq.length`/`Seq.get`).
- `src/pycsl/module6_whyml/preamble.py` — `list_comp_seq_<τ>` vals (on demand).
- `src/self-annotate/src/module6_whyml/statements.py` — the un-`\trust` edit + frame.

---

## 4. Out-of-scope / soundness boundary

- **Only reassigned/grown list locals become `seq`** — a NON-reassigned array local (e.g.
  `tuple_unpack`'s `targets`, indexed but never reassigned) STAYS `array` (byte-identical; the
  `array`-based L1–L7 machinery is untouched). The promotion is keyed on a *reassignment*.
- **`seq` content is opaque** where the source op is (`snapshot`, `list_comp_seq`); the length
  law is the only claim. `ensures True` + frame, not value-faithful.
- **Corpus untouched** — @mutable_state + element-type-map gated; byte-diff 0 is the proof.
- **Faithful:** `seq` IS Python-list value-semantics (a slice/reassign produces a new value) —
  arguably MORE faithful than the mutable `array` for a reassigned local.

---

## 5. Reference corpus (required)

Add to `test-suite/corpus/pycsl-reference/` + a mirror witness:
- `seq-reassign-witness.py` — a `@mutable_state` method with `xs = self.d.get("k", []); xs =
  xs[:-1]; xs[-1]` — the reassign+slice+index pattern binding a `seq`.

---

## 6. Verification (exact commands)

```bash
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/statements.py --import-path src/pycsl --no-proof
.venv/bin/python src/pycsl/pycsl.py \
  src/self-annotate/src/module6_whyml/statements.py --import-path src/pycsl        # full proof
PYTHONHASHSEED=0 bash bin/byte-diff-sweep.sh /tmp/after && diff -rq <baseline> /tmp/after
bash bin/run-self-annotation-suite.sh    # only pre-existing errors.py may fail
```

---

## 7. Definition of done

- SQ1–SQ5 landed; reassignable list locals are `seq`; `body_stmts[:-1]` no longer aliases;
  `_handle_critical_section_stmt` un-`\trusted` with a checked frame.
- **12 real emitter handlers verify their own body-faithfulness** — the reflecting-family
  trusted base EMPTY.
- Byte-diff 0; suite green; `self-ir-schema.md` §8 (IR5) closed.

---

## 8. Execution log — DONE. `_handle_critical_section_stmt` un-`\trusted` (the 12th handler)

**ALL 12 reflecting-family emitter handlers now verify their own body-faithfulness.**
Full proof SUCCESS; byte-diff 0 across the 627-corpus; expressions.py mirror still PASSES.

- **SQ1** — a REASSIGNED list-elem local (`body_stmts`, assigned >1×) is promoted to
  `_seq_locals` with its element value type (dropped from `_array_elem_types`).
- **SQ2** — POLYMORPHIC `snapshot : array 'a → seq 'a` in @mutable_state modules; the
  `List[StmtIR]` field read `body_stmts = stmt.body` → `ref (snapshot stmt.body)` (`seq emit_ir`).
- **SQ3** — `body_stmts[:-1]` → `seq_sub` (a pure seq sub-sequence, NO `array_slice`/region —
  the reassignment alias is GONE); `body_stmts[-1]` → `Seq.get` (recognized emit_ir via
  `_seq_value_types`); `_seq_operand` passes a seq slice through without `snapshot`.
- **SQ4** — the seq comprehension: `[s.to_dict() for s in body_stmts]` re-materialises a stmt
  list → `list_comp_stmts (src: seq 'a) : array int` (unifies with `_stmts_to_whyml`'s `array
  int` param); a general seq comprehension → `list_comp_seq_<τ> : seq <τ>`.
- **SQ5** — `assigns self._havoc_counter, self._in_spec` (the checked frame); a @mutable_state
  for-loop carries `invariant { 0 <= idx }` + `variant { len - idx }` so the element-read
  bounds and termination discharge (the same loop-invariant discipline tuple_unpack needed).

**The `array`→`seq` insight:** a Python list that is REASSIGNED is a *value*, not a mutable
region — Why3's immutable `seq` is the faithful model (and the one that type-checks). This is
arguably MORE faithful than the mutable `array` for a reassigned local.

**12 of 12 — the reflecting-family trusted base is EMPTY.** The entire body-faithful-emitter
arc (`typed-ir-for-b-ceiling` → `i-feel-good` → `list-comprehension-lowering` → `self-ir-schema`
→ `seq-model-pivot`) is complete: every reflecting `_handle_*` statement handler proves its own
body.
