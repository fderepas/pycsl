# Faithful string-op modeling — project specification

**Status:** IMPLEMENTED (P1–P4). See §9 for the as-built notes (a few choices deviated
from this draft — all toward more rigor or a cleaner outcome).
**Owner:** Module 6 (WhyML lowering) + reference corpus.
**Doctrine:** [no-more-int] — lower each Python string operation to its faithful
`string`-typed WhyML form, not an opaque `int`. Reject value→int coercions.
**Motivates:** `typed-ir-for-b-ceiling.md` §22 — `_handle_expr_stmt` (and the string-
building inside `_handle_ghost_assign_stmt` / `_handle_critical_section_stmt`) stalls on
`arr_name = func.rsplit(".", 1)[0].replace(".", "_")` lowering to opaque `int`, so
`whyml_ident(arr_name)` (which wants `string`) fails to type-check.

---

## 1. Problem

The verifier already models a handful of string operations faithfully — `str_sub_op`
(substring), `str_length_op` (`len`), `str_hash_op` (dict key), `str_repr_op` (`repr`),
`str_to_int` (`int(s)`). But the emitter (and real programs) use a wider set of string
methods to BUILD strings — `.replace`, `.rsplit`/`.split` (+ element indexing),
`.strip`/`.lstrip`/`.rstrip`, `.lower`/`.upper`, `.join`. These currently lower to an
**opaque `int`** (the pre-no-more-int default), so any downstream use in a `string`
context is a type error.

### 1.1 Why this is its own project (not a byte-clean gate)

Unlike the `typed-ir-for-b-ceiling.md` features (§18–§21), which are gated on
`@mutable_state` and are byte-identical for the corpus, faithful string ops are
**CORPUS-AFFECTING**: these methods appear in *real* programs today and currently emit
opaque int. A faithful `string` model changes their emitted bytes. So the gate is not
"byte-diff 0" but "**the corpus still VERIFIES, and the reference corpus grows**".

### 1.2 Audited usage (as of this spec)

Fixed-string occurrences under `test-suite/` (real programs) and `src/pycsl/module6_whyml/`
(the self-annotation driver):

| op | test-suite | module6_whyml | current lowering |
|----|-----------:|--------------:|------------------|
| `.join(`   | 18 | 91 | opaque int / `join_array` (int) |
| `.strip(`  |  7 | — | opaque int |
| `.replace(`|  6 | 24 | opaque int (note: `datetime.replace`/`dataclasses.replace` are NON-string module fns — exclude) |
| `.split(`  |  6 | 39 | int LENGTH (`len(s.split(sep))`, `python-reference/.../split_proves.py`) |
| `.lower(`  |  5 | — | opaque int |
| `.rsplit(` |  1 | 17 | opaque int |

Emitter idiom forms that must lower faithfully (from `statements.py`):
- `func.rsplit(".", 1)[0]` — head before the last `sep`.
- `func.rsplit(".", 1)[1]` — tail after the last `sep`.
- `func.replace(".", "_")` — character-for-character substitution.
- `stripped.replace("_", "").replace("!", "").isalnum()` — replace-chain then predicate.

---

## 2. Design principle — SOUND laws, never over-claim

Every op is an abstract `val` whose `ensures` states only facts that hold for EVERY input
— exactly like the existing ops. The model for the discipline:

```
val str_sub_op (s: string) (lo len: int) : string
  ensures { result = (String.substring s lo len) }
  ensures { (0 <= lo /\ 0 <= len /\ lo + len <= String.length s)
            -> String.length result = len }
```

```
val str_repr_op (s: string) : string
  ensures { String.length result >= 2 }   (* NOT a +2 equality — would be unsound *)
```

`str_repr_op` is the cautionary tale: `repr` adds two quote chars ONLY for escape-free
strings, so an exact-length law would be UNSOUND; the only universally-true fact is the
lower bound. Every op below is specified the same way — the STRONGEST law that is still
sound for all inputs, and no stronger.

**Available Why3 theory:** `string.String` (`String.length`, `String.substring`,
`String.concat`) and `string.Char`. Where `String` has no primitive (there is no
`String.replace`/`String.split`), the op is abstract with a length-relation `ensures`
rather than a definitional one — sound, and enough to type-check + carry length facts.

---

## 3. The operations

### 3.1 `str.replace(old, new)` — `str_replace_op`

```
val str_replace_op (s old new: string) : string
  ensures { String.length old = String.length new
            -> String.length result = String.length s }
```

- **Sound law:** character-for-character replacement (`len old = len new`) preserves
  length. In general `.replace` may grow/shrink the string (e.g. `"".replace("","x")`),
  so NO unconditional length law is sound — only the equal-length case.
- **Covers the emitter idiom** `func.replace(".", "_")` (single char → single char):
  the conditional fires (`len "." = len "_" = 1`), so the result is `string` of the same
  length — enough for `whyml_ident`.
- **Chained** `x.replace(a,b).replace(c,d)` composes (each returns `string`).
- Recognizer: `_handle_call_expr`, method `replace`, 2 string args, string receiver.

### 3.2 `str.lower()` / `str.upper()` — `str_case_op`

```
val str_case_op (s: string) : string
  ensures { String.length s >= 1 -> String.length result >= 1 }
```

- **SOUNDNESS CAVEAT (a `str_repr_op`-class trap).** Case folding is NOT length-preserving
  in Python's Unicode model: `"ß".upper() == "SS"` (1→2), `"İ".lower() == "i̇"` (1→2). So
  `String.length result = String.length s` would be **UNSOUND** — do NOT emit it. Case
  folding never maps a non-empty string to empty, so the only universally-true fact is the
  non-emptiness lower bound above. (If PyCSL later restricts to an ASCII string class, the
  equality law becomes sound *for that class* and can be added conditionally.)
- One op for both `lower` and `upper` (the sound law is identical; content is unmodeled).
- **Consequence:** a receiving local still types as `string` (the goal), but a caller
  gets no exact-length fact — acceptable, and honest.

### 3.3 `str.strip()` / `lstrip()` / `rstrip()` — `str_strip_op`

```
val str_strip_op (s: string) : string
  ensures { String.length result <= String.length s }
```

- **Sound law:** stripping only removes chars → result is no longer than the input.
- Optional-arg forms (`strip(chars)`) share the op (the law is the same).

### 3.4 Split-element idioms — `str_split_elem_op`

`str.split(sep)` / `str.rsplit(sep, k)` return a LIST. The existing model keeps
`len(s.split(sep))` as a non-negative int (KEEP — see §5). What is missing is the
STRING-valued ELEMENT read `s.split(sep)[i]` / `s.rsplit(sep, k)[i]`:

```
val str_split_elem_op (s sep: string) (i: int) : string
  ensures { String.length result <= String.length s }
```

- **Sound law:** every split piece is a substring of `s` (separators are removed) → no
  piece is longer than `s`.
- **Covers** `func.rsplit(".", 1)[0]` and `func.rsplit(".", 1)[1]` — both lower to
  `str_split_elem_op func "." 0` / `… 1`. (A negative index `[-1]` maps to the last
  piece; since content is unmodeled, `[-1]` and `[1]`-after-`rsplit(sep,1)` both use the
  same op — the length law holds regardless of `i`.)
- Recognizer: a `Subscript` whose `value` is a `.split`/`.rsplit` Call on a string
  receiver → `str_split_elem_op`. (Mirrors the B-C5 `arg0_of` idiom recognizer.)

### 3.5 `sep.join(parts)` — `str_join_op` (PHASE 4, hardest)

`.join` takes an ITERABLE of strings. Two sub-cases:
- **Literal/known-arity** `sep.join([a, b, c])` — lower to nested `String.concat` with
  `sep` between: `concat a (concat sep (concat b (concat sep c)))`. FAITHFUL and exact.
- **General** `sep.join(xs)` over an opaque sequence — abstract:
  ```
  val str_join_op (sep: string) (xs: <seq string>) : string
    ensures { True }   (* no universally-sound non-trivial length law without |xs| *)
  ```
  A length law needs the element count and per-element lengths; if the sequence length
  `n` is available, `String.length result >= (n-1) * String.length sep` is sound and can
  be added. Deferred until a `seq string` element-model exists (interacts with the
  list-local work in §21 / tuple_unpack).

---

## 4. Tool changes (per op)

All in `src/pycsl/module6_whyml/expressions.py` (`_handle_call_expr` for the method calls;
`_handle_subscript` for the split-element idiom), mirroring the existing `str_sub_op` /
`str_hash_op` recognizers:

1. Recognize the method/idiom on a **string receiver** (`self._is_string_expr(recv)`),
   NOT in `_in_spec` where the definitional Why3 term is used directly if one exists.
2. `self._add_abstract_op("val …")` with the §3 signature + `ensures`.
3. Return the applied op string; the RESULT is a `string`, so `_is_string_expr` /
   `_ret_of` must report `string` for these method calls (so a receiving local types as a
   string local — reuses the `_string_local_vars` / L2 machinery, no new local kind).
4. Spec context (`_in_spec`): `replace`/`case`/`strip`/`split_elem` have no `String.*`
   primitive, so the abstract op is used in specs too (its `ensures` is the only law);
   `join` of a literal uses `String.concat` directly in specs.

---

## 5. What NOT to change

- **`len(s.split(sep))` stays int.** `split` returns a list; its LENGTH is an honest
  non-negative int and `python-reference/.../split_proves.py` depends on it. The
  string-element op (§3.4) is ADDITIVE — it does not touch the length model.
- **`join_array (a: array int) : int`** (the existing int-join over int arrays) is a
  DIFFERENT op (numeric) — untouched.
- **`datetime.replace` / `dataclasses.replace`** are module functions, not `str.replace`
  — the recognizer must gate on a **string receiver**, or these regress.

---

## 6. Phasing & gating

Total additivity per phase: every existing corpus proof still VERIFIES, and each phase
adds reference tests. Because this is corpus-affecting, each phase regenerates the affected
`.mlw` baselines and RE-VERIFIES (not byte-diff 0).

| Phase | Ops | Unblocks | Risk |
|-------|-----|----------|------|
| **P1** | `.replace` (§3.1), `.lower`/`.upper` (§3.2) | `expr_stmt`'s `arr_name` chain; the clean length-law ops | low |
| **P2** | split-element `str_split_elem_op` (§3.4) | `func.rsplit(".",1)[0]`/`[1]`; `.split(sep)[i]` | low |
| **P3** | `.strip` family (§3.3) | real-program `.strip()` | low |
| **P4** | `.join` (§3.5) | literal-join exact; general-join deferred to `seq string` | med/high |

**Per-phase gate (all must hold):**
1. `python3 -c "import ast; ast.parse(...)"` on every touched tool file.
2. `bin/byte-diff-sweep.sh` — inspect the diff; it will be NON-empty (corpus-affecting).
   For each changed `.mlw`, confirm the file still VERIFIES (`pycsl <file>` → SUCCESS).
3. New reference programs under `test-suite/corpus/pycsl-reference/` (a `_proves.py` and a
   `_fails.py` per op — the [reference-corpus] requirement), each exercising the op's
   `ensures` law (e.g. `str_case_op` proves `len(s.lower()) == len(s)`; a `_fails.py`
   asserting `len(s.lower()) == len(s) + 1` must NOT verify — non-vacuity).
4. A witness under `src/self-annotate/` if the op is used by an emitter handler.

---

## 7. Acceptance

- **Feature-level:** all of P1–P3 landed; `str.replace`/`.lower`/`.upper`/`.strip`/
  split-element read as faithful `string` (not opaque int), with sound length laws.
- **Handler-level (the motivation):** with P1+P2, `_handle_expr_stmt`'s
  `arr_name = func.rsplit(".", 1)[0].replace(".", "_")` type-checks (`arr_name : string`),
  clearing its first blocker. `expr_stmt` then continues into its Call-reflection tail
  (B-C5, already landed) — a separate un-`\trusted` acceptance tracked in
  `typed-ir-for-b-ceiling.md`.
- **Corpus:** the full suite still green; reference corpus grows by ≥ 2 files per op.

---

## 8. Risks & open questions

- **`.replace` unconditional length.** Only the equal-length case is sound. If a handler
  needs a length fact for an unequal-length replace, none is available — acceptable
  (the emitter's replaces are all char-for-char).
- **`.join` general case (P4).** Needs a `seq string` element model, which overlaps the
  list-local / comprehension work (`typed-ir-for-b-ceiling.md` §21). Sequencing: do the
  `seq string` model there, then P4 here. Until then, only literal joins are faithful.
- **Content is never modeled.** These ops carry LENGTH relations only (like `str_repr_op`).
  A postcondition about the CONTENT of a replaced/split/joined string remains honestly
  unprovable — the faithful model, not a trusted lie. Callers needing content facts must
  use `_in_spec` definitional forms where a `String.*` primitive exists (only `concat`).
- **`_is_string_expr` reach.** Chained idioms (`x.replace(a,b).replace(c,d)`,
  `s.rsplit(sep,1)[0].replace(a,b)`) require `_is_string_expr` / `_ret_of` to report
  `string` for each link so the OUTER op sees a string receiver — verify the recognizer
  composes (it does for `str_sub_op` today).

---

## 9. As-built notes (implementation)

All four phases are implemented in `src/pycsl/module6_whyml/expressions.py` (recognizers +
faithful ops) and `statements.py` (string-local recognition), with 10 reference tests
under `test-suite/corpus/python-reference/stdlib/str_methods/` and an emitter witness
`src/self-annotate/faithful-string-op-witness.py`. Choices that deviated from the draft:

1. **`old`/`new` are Why3 RESERVED keywords.** `str_replace_op`'s params are named
   `(s pat rep: string)`, not `(s old new: string)` — the latter is a syntax error.
2. **The feature is BYTE-CLEAN, not corpus-affecting.** §1.1 assumed a faithful model
   would change corpus bytes. It does NOT: `bin/byte-diff-sweep.sh` shows **diff 0** across
   all 627 files after all four phases. The corpus's `.replace`/`.strip`/`.lower`/`.split`/
   `.join` are the excluded `datetime`/`dataclasses.replace` module forms, or on receivers
   the recognizers correctly do not fire on, or simply absent from the emitting path. So
   the gate SIMPLIFIED to byte-diff 0 + reference tests + handlers green (stronger than the
   planned "corpus still verifies"). Non-vacuity is proven by the reference `_proves`/
   `_fails` pairs and the probes, not by corpus deltas.
3. **`.strip` (draft P3) was folded into P1.** `str_strip_op` sits in the same
   `_handle_string_value_method` dispatch as `.replace`/`.lower`/`.upper`; there was no
   reason to stage it separately. So the landed order is P1 (replace/case/strip) → P2
   (split-element) → P4 (literal join); the draft's P3 is subsumed.
4. **Split-element `[-1]` and `[1]`** share `str_split_elem_op` (content unmodeled, so the
   `<= len s` bound holds for any index) — as the draft anticipated.
5. **`.join` — literal receiver-form only.** `_handle_join_call` lowers a LITERAL
   list/tuple of strings joined by a literal/computed `sep` (the `receiver` form,
   e.g. `",".join([a, b])`) to nested `str_concat_op` — EXACT length
   (`sum(len eᵢ) + (n-1)·len sep`, proven by `join_proves.py`). A VAR-sep join
   (`sep.join([...])` where `sep` is a variable → dotted `func="sep.join"`, no `receiver`)
   and a general/computed iterable stay on the opaque int `join_array`/`join_1` — deferred
   to a `seq string` model (§3.5, §8), unchanged.

**String-local reach (the acceptance path).** The string-local recognizer's `_is_str_val`
(`statements.py`) was extended so a local bound from a faithful string op is a STRING local
(pre-decl `ref ""`) OUTSIDE `@mutable_state` too — scoped to the new ops (`_is_str_value_
method` + split-element), not the whole `_is_string_expr`, to keep byte-diff 0. This is
what makes `arr_name = func.rsplit(".", 1)[0].replace(".", "_")` type-check
(`arr_name : string`), clearing `_handle_expr_stmt`'s first blocker (verified end-to-end).

**Verification summary.** 10/10 reference tests behave correctly under `--proof` (5 sound
laws Valid; 5 unsound claims Unknown/Timeout — non-vacuous). Byte-diff 0. The 7
self-annotated handlers + all emit_ir/collision witnesses stay green. Self-annotation
suite unchanged (only the pre-existing `errors.py` fails).

**Sound laws as landed:** `str_replace_op` (equal-length ⇒ length preserved),
`str_case_op` (non-emptiness bound only — Unicode-safe), `str_strip_op` (`≤ len s`),
`str_split_elem_op` (`≤ len s`), `str_concat_op` (exact `len a + len b`, reused for join).
