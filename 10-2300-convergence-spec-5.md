STATUS: DONE

<!-- COORDINATION APPROVAL (editorial). The plan is sound; the key finding is the win: the round-trip is a
THEORY LEMMA, not an axiom. Risk rulings:
- R1 (TCB): APPROVED — `string.Char` is a sibling module in the SAME trusted Why3 stdlib `string.mlw` as
  `string.String` (already in the TCB). Relying on its `chr_code`/`code`/`code_chr` axioms adds NO new TCB
  and needs NO cross-validated Rocq/Lean axiom. Drop the gap's §1 axiom proposal — use the theory lemma.
- R2 (0..255 bounds): APPROVED, and it is FAITHFUL, not a narrowing — Unix filenames are byte strings and
  Why3's `char` is a byte (`axiom code: 0 <= code c < 256`). `ord_op : 0..255` is exactly the on-disk byte.
  (A Python str with a code point >255 is already outside Why3's byte-string model — a pre-existing string
  limitation, not introduced here; out of scope.)
- R3 (_coerce_to_int defensive edit): APPROVED — DEFER. The `ord`/`chr` handlers fix the bug by never
  reaching the generic path; do not touch `_coerce_to_int` (keeps the corpus byte-identical).
- R4 (prover + corpus): APPROVED — pin Alt-Ergo for the round-trip goal; include the reference-corpus driver
  in this iteration (new-feature corpus rule).
Acceptance bar: full-corpus byte-diff IDENTICAL (additive; fires only for ord/chr calls); conformance 38/38;
os byte-identical; the `chr(ord(c)) == c` round-trip driver PROVES (Alt-Ergo); doc-coherency green. On
success set STATUS: DONE. -->

# Convergence spec — iteration 5: the `ord`/`chr` char↔int bridge

Pairs with the gap document `10-2300-convergence-gap-5.md` (`STATUS: OPEN`).
Stamp `10-2300`, iteration `N = 5`. This is a SPEC-PHASE document: it specifies the
implementation but contains NO source edits. Implementation follows after the
coordination agent sets `STATUS: APPROVED`.

---

## 1. Preamble — the gap and the char↔int need

The string-domain directory-entry name codec (`decode(encode(name)) == name`) already
PROVES in place (`pure_lib/os/UnixInodeFileSystem.py`, standalone proof
`pure_lib_test/probe_namecodec_leaf.py`, all VCs Valid, zero `\trusted`, zero axioms).
The remaining leaf is the BYTE side: the on-disk dirent name field is 30 *bytes*, and the
faithful byte codec needs `b[i] = ord(name[i])` to encode and rebuild the string via
`chr(...)` to decode. That requires a char↔int bridge:

- `ord(name[i])` — a 1-char string → its code point (an `int`).
- `chr(b)` — an `int` → a 1-char string.
- the round-trip `chr(ord(c)) == c` (for a 1-char string `c`) and `ord(chr(n)) == n`
  (for a code point `n` in range).

Today `ord` on a string fails WhyML type-check ("has type string, but is expected to have
type int"). Root cause (cited in the gap): `ord` is not a recognized builtin, so it falls
through to the generic unannotated-callee path at
`src/pycsl/module6_whyml/expressions.py:1073-1092`, which declares
`val ord_1 (x0: int) : int` — assuming every argument is `int`; and `_coerce_to_int`
(`expressions.py:150-182`) leaves a non-literal `string` expression untouched
(`return whyml_str`, line 182). So the `string` from `name[i]` flows into an `int`-typed
parameter → the type error. `name[i]` already lowers to `(str_sub_op name i 1) : string`
(`expressions.py:1625-1637`); that is the correct input shape — the only missing piece is a
typed `string → int` op (`ord`) and `int → string` op (`chr`).

---

## 2. THE KEY FINDING — the round-trip comes FREE from the existing Why3 theory (NO new axiom)

**TCB decision resolved in favour of NO new axiom.** This is the single most important
finding of this spec.

PyCSL emits `use string.String` (`preamble.py:370`). The active Why3 stdlib
(`why3 config`: loadpath
`/home/fabrice.derepas@canonical.com/.opam/coq-4.14/share/why3/stdlib`) ships
`string.mlw`, which contains — in addition to module `String` — a module **`Char`**
(`stdlib/string.mlw:389-452`). That module already provides EXACTLY the char↔int primitives
and round-trip we need, as AXIOMS OF THE THEORY (not facts we must add):

```
(stdlib/string.mlw)
389  module Char
395    type char = abstract { contents: string } invariant { length contents = 1 }
404    function code char : int
406    axiom code:     forall c. 0 <= code c < 256
408    function chr (n: int) : char
410    axiom code_chr: forall n. 0 <= n < 256 -> code (chr n) = n
412    axiom chr_code: forall c. chr (code c) = c          <-- round-trip B, FREE
414    function get (s: string) (i: int) : char
417    axiom get:      forall s i. 0 <= i < length s -> (get s i).contents = s_at s i
439    axiom extensionality: forall s1 s2. eq_string s1 s2 -> s1 = s2
```

So the round-trip `chr(code(c)) == c` is `axiom chr_code` (string.mlw:412) and
`code(chr(n)) == n` (for `0 <= n < 256`) is `axiom code_chr` (string.mlw:410). These are
ALREADY in the trusted base of the upstream Why3 string theory PyCSL already uses — adopting
`use string.Char` adds **no PyCSL-owned axiom** to the TCB. It only widens reliance from
`String` to `String + Char` within the same already-trusted `string.mlw` file.

### Probe evidence (hand-written `.mlw`, `why3 prove`)

The char-level round-trip is proved directly from the theory axioms
(`/tmp/probe_char.mlw`): `chr (code c) = c`, `0 <= n < 256 -> code (chr n) = n`, and
`0 <= code c < 256` are all **Valid** (z3 ~1041 steps; alt-ergo ~12 steps each).

PyCSL works with 1-char `string`s (from `str_sub_op = substring`), not the abstract `char`
type, so the bridge composes `code`/`chr` with `get`/`.contents`. The STRING-LEVEL
round-trip was probed with the actual emission shape (`/tmp/probe_str.mlw`,
`/tmp/probe_pycsl_shape.mlw`, `/tmp/probe_preamble.mlw`), defining

```
ord(c) := code (get c 0)      chr(n) := (chr n).contents
```

Results (all **Valid**, NO added axiom):

| goal | meaning | alt-ergo |
| --- | --- | --- |
| `length (chr n) = 1` | chr yields a 1-char string | 27 steps |
| `0 <= ord c < 256` | ord range | 30 steps |
| `0 <= n < 256 -> ord(chr n) = n` | round-trip A | 1732 steps |
| `length c = 1 -> chr(ord c) = c` | round-trip B | 237 steps |

The realistic-preamble probe (`/tmp/probe_preamble.mlw`: `use string.String` + `use
string.Char` together, `str_sub_op`, total `ord_op`/`chr_op`, plus the gap's `probe_c`
function and the `chr(ord(name[0])) == name[0]` driver) is **Valid** for both VCs (alt-ergo
10 and 122 steps). `String` and `Char` coexist with no name clash in the same `use` block.

> Note (Z3 cost): round-trip B is heavy for Z3 alone (~4s, ~3.5M steps via the `string.Char`
> extensionality axiom at string.mlw:439). Alt-Ergo discharges it in 237 steps. PyCSL runs
> both solvers, so this is not a blocker, but the gate (§4) should pin Alt-Ergo for the
> round-trip driver.

**Conclusion: the round-trip is a THEORY LEMMA, not a new axiom. No `_AXIOM_REGISTRY` entry,
no paired Rocq/Lean proof, no TCB growth beyond `use string.Char`.** (The gap's "Proposed
fix" §1 suggested a cross-validated round-trip axiom; this spec supersedes that — the axiom
is unnecessary because the theory already proves it.)

---

## 3. The `ord_op` / `chr_op` design

Two abstract `val`s, emitted on demand (only when `ord`/`chr` is actually called), gated
behind a flag that also forces `use string.Char` into the preamble. Both are TOTAL (no
precondition) — this is the cleanest shape and was probed Valid:

```whyml
val ord_op (c: string) : int
  ensures { 0 <= result < 256 }
  ensures { result = code (get c 0) }

val chr_op (n: int) : string
  ensures { length result = 1 }
  ensures { result = (chr n).contents }
```

Design rationale:

- **`ord_op` total (no `requires length c = 1`).** `get c 0` is total in the theory
  (returns a `char`, whose invariant forces `length contents = 1`), so no precondition is
  needed to type-check. The round-trip `chr(ord c) = c` holds only when `length c = 1`;
  that obligation is discharged at the CALL SITE from the caller's own facts (e.g.
  `length name >= 1` makes `length (substring name i 1) = 1`). Probed: the call-site VC
  `test_b` is Valid (alt-ergo 206 steps). Making `ord_op` total avoids threading a
  precondition through the emitter and keeps the existing builtin-dispatch shape.
- **`ord_op` range `0 <= result < 256`.** Matches `axiom code` (string.mlw:406). This is the
  faithful range for the dirent use (bytes 0..255). The gap's `probe_c` wants
  `0 <= \result <= 255`, which follows directly (`< 256` ⟺ `<= 255` on int).
- **`chr_op` ensures `length result = 1`** ties `chr`'s output to a genuine 1-char string,
  so downstream `_is_string_expr` length reasoning (e.g. `len(chr(b)) == 1`) holds, and the
  result is a valid input to `ord_op`/string ops.
- The two `result = code (get c 0)` / `result = (chr n).contents` ensures are what make the
  round-trips provable; they are pure theory references, no new trust.

Both ops are idempotent-registered via `_add_abstract_op` (the existing dedup mechanism used
by `str_sub_op`, `str_repr_op`, etc.), so repeated `ord`/`chr` calls emit one declaration
each.

### Preamble wiring

When `ord`/`chr` fires, the preamble must add `use string.Char` after the existing
`use string.String` (`preamble.py:370`). Probed: the two coexist with no clash. Wiring
options (implementation phase to pick):

- add a `needs_char` flag to the `needs` dict computed before `_emit_preamble_uses`, set
  when the emitter registers `ord_op`/`chr_op`, and emit `use string.Char` under the same
  `if` that emits `use string.String` (string.Char already `use`s String); OR
- since `ord_op`/`chr_op` reference `code`/`chr`/`get`/`.contents`, fold them into the
  existing `needs_string` predicate so any program using them also pulls `string.Char`.

Prefer a dedicated `needs_char` so the byte-additivity guarantee (§4) is exact: programs
that never call `ord`/`chr` get a byte-identical preamble (no spurious `use string.Char`).

---

## 4. The emitter edits (file:line)

All edits are in `src/pycsl/module6_whyml/expressions.py` plus one preamble flag in
`preamble.py`. No edits in this phase — these are the targets for the implementation phase.

### 4.1 Add the `ord`/`chr` cases in `_call_named_builtins`

`_call_named_builtins` (`expressions.py:1194`) is the right place — it is dispatched from
`_handle_call_expr` (`expressions.py:1061-1064`) BEFORE the generic unannotated-callee path
(`expressions.py:1073-1092`) that currently mis-types the arg. Add, alongside the existing
`len`/`str`/`hash` cases (e.g. near the `str`/`repr` block at `expressions.py:1367-1393`):

```python
if func_name == "ord" and len(args) == 1:
    arg_ir = expr.get("args", [{}])[0] if expr.get("args") else {}
    if self._is_string_expr(arg_ir):
        self._note_needs_char()            # set the needs_char flag (preamble)
        self._add_abstract_op(
            "val ord_op (c: string) : int\n"
            "    ensures { 0 <= result < 256 }\n"
            "    ensures { result = code (get c 0) }")
        return f"(ord_op {args[0]})"
    # non-string ord(x): fall through (return None) — keep current behaviour.

if func_name == "chr" and len(args) == 1:
    self._note_needs_char()
    self._add_abstract_op(
        "val chr_op (n: int) : string\n"
        "    ensures { length result = 1 }\n"
        "    ensures { result = (chr n).contents }")
    return f"(chr_op {args[0]})"
```

`args[0]` for `ord` is already the lowered 1-char string `(str_sub_op name i 1)`
(`expressions.py:1625-1637`) — the correct input shape, confirmed by the `/tmp/probe_preamble.mlw`
probe. `args[0]` for `chr` is the lowered int operand. (`_note_needs_char` is a thin
setter — implementation may instead set a transpiler attribute the preamble reads.)

### 4.2 Result-typing: `chr(...)` is a string, `ord(...)` is an int

`_is_string_expr` (`expressions.py:334-365`) decides whether a `Call` node is string-typed.
Its `Call` branch (`expressions.py:362-364`) currently only consults
`_module_method_return_annotations`. Add a builtin-name check so `chr(...)` is recognized as
string-typed:

```python
if t == "Call":
    fn = ir.get("func", "")
    if fn == "chr":
        return True
    return getattr(self, "_module_method_return_annotations", {}).get(fn) == "str"
```

This makes `len(chr(b))`, `s + chr(b)`, `chr(b) == c`, and `chr(...)` as a subscript base all
route through the real string bridges rather than the opaque int fallback.

`ord(...)` returns `int`; the default `Call` → `False` is already correct (no edit needed for
ord in `_is_string_expr`).

### 4.3 Defensive `_coerce_to_int` (optional, recommended)

The gap's §2 root cause is that a non-literal `string` expression passed where `int` is
expected falls through `_coerce_to_int` unchanged (`expressions.py:182`). With §4.1 in place,
`ord`/`chr` never reach the generic path, so the immediate bug is fixed. As defence-in-depth
(so the generic path can NEVER again emit an int-param applied to a string), `_coerce_to_int`
MAY route a `string`-shaped non-literal operand through `ord_op` — but this is a behaviour
change to the generic path and risks byte-diffs. RECOMMENDATION: leave `_coerce_to_int`
unchanged in this iteration (byte-additivity is paramount, §4 gate); revisit as a separate
hardening item if the generic-path string leak recurs. Flagged to the coordination agent.

---

## 5. Byte-additivity, test drivers, and gate plan

### 5.1 Byte-additivity

The `ord`/`chr` cases fire ONLY for `ord(...)`/`chr(...)` calls. The proving corpus and the
conformance suite contain no such calls (to be confirmed in the gate: grep the corpus). With
a dedicated `needs_char` flag (§3), programs that never call `ord`/`chr` get a byte-identical
preamble and body. Existing emission MUST be byte-IDENTICAL.

### 5.2 Test drivers

- **Round-trip driver** (new, under `pure_lib_test/`): a 1-char-string round-trip
  `chr(ord(c)) == c`, e.g.:
  ```python
  #@ requires \str_length(name) >= 1
  #@ assigns \nothing
  #@ ensures \result == name[0:1]
  def probe_chr_ord_roundtrip(name: str) -> str:
      return chr(ord(name[0]))
  ```
  MUST PROVE (Alt-Ergo). Probed analogue Valid (`/tmp/probe_preamble.mlw` `roundtrip`,
  122 steps). The exact PyCSL surface for the postcondition (`name[0:1]` vs `name[0]`) is to
  be matched to how `_is_string_expr`/slice lowering produces `substring name 0 1`.
- **`probe_c.py`** (existing gap reproducer, `pure_lib_test/probe_c.py`): `ord(name[0])` with
  `ensures 0 <= \result <= 255` — must now EMIT and PROVE (was the type-error wall).
- **Reference-corpus driver** (per the reference-corpus requirement memory): add a small
  `ord`/`chr` round-trip test under `test-suite/corpus/pycsl-reference/` so the feature is
  covered by the standing corpus, not only an ad-hoc probe.

### 5.3 Gate plan

1. Full-corpus byte-diff IDENTICAL (the byte-additivity gate; `bin/extraction-byte-diff*.sh`).
2. Conformance 38/38.
3. `os` byte-identical (the os codec still emits its current string-view shape until the
   byte codec is wired in a later iteration; this iteration only adds the bridge).
4. Round-trip driver proves (Alt-Ergo); `probe_c.py` proves.
5. Reference-corpus `ord`/`chr` test proves.
6. Doc-coherency green (`bin/doc-coherency.py --check`) — `ord`/`chr` are builtins, not
   `#@` directives, so this should be unaffected, but run it to confirm no drift.

---

## 6. RISKS / open questions for the coordination agent

1. **TCB: theory-lemma vs new-axiom — RESOLVED to LEMMA (lead item).** The round-trip
   `chr(ord(c)) == c` / `ord(chr(n)) == n` falls out of the EXISTING Why3 `string.Char`
   theory (`stdlib/string.mlw:410-412`), proved directly by the probes (§2). We adopt
   `use string.Char` — which only widens reliance to a sibling module of the already-used
   `string.mlw`. **No PyCSL-owned axiom, no `_AXIOM_REGISTRY` entry, no paired Rocq/Lean
   proof required.** This supersedes the gap's "Proposed fix §1" (which proposed a
   cross-validated round-trip axiom). Coordination judgment needed: confirm that relying on
   `string.Char`'s axioms (already part of the upstream string theory) is acceptable without
   a separate TCB sign-off, given PyCSL already trusts `string.String` from the same file.

2. **Does Why3's string theory expose chars? — YES.** Module `Char` exists in the active
   stdlib (`stdlib/string.mlw:389`) with `type char`, `code`, `chr`, `get`, extensionality.
   So the abstract-op + new-axiom route (which Risk 1 would have forced if only `string`
   were available) is NOT needed. (If a future Why3 upgrade dropped `string.Char`, the
   fallback would be the new-axiom route — flagged for awareness, not action.)

3. **Bounds: 0..255, not 0..0x10FFFF.** The dirent stores BYTES, and `axiom code`
   (string.mlw:406) pins `0 <= code c < 256`. `ord_op` therefore ensures `0 <= result < 256`
   (⟺ `<= 255`). This is faithful for the byte/dirent use and matches the gap's
   `probe_c` (`<= 255`). Open question: full Python `ord` ranges to 0x10FFFF for non-byte
   strings; modelling `ord` as 0..255 is SOUND for the byte codec but is a NARROWING of
   Python's general `ord`. If a future caller needs the full code-point range, `ord_op`'s
   `< 256` ensures would be too tight. RECOMMENDATION: ship the 0..255 model now (matches the
   theory's `code` axiom and the dirent need); document the narrowing. Coordination judgment:
   accept the 0..255 narrowing for this iteration?

4. **Z3 cost on round-trip B** (~4s via extensionality). Alt-Ergo is fast (237 steps). PyCSL
   runs both — not a blocker, but the round-trip driver gate should pin Alt-Ergo. Low risk.

5. **`_coerce_to_int` defensive edit (§4.3) — deferred.** Routing generic-path string
   operands through `ord_op` risks corpus byte-diffs. Recommend leaving it unchanged this
   iteration. Coordination judgment: defer the defensive hardening?

6. **Reference-corpus addition.** Per the reference-corpus memory requirement, a corpus test
   is part of this feature. Confirm the coordination agent wants it landed in the same
   iteration as the emitter edits (recommended) vs deferred.
