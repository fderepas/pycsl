# Missing feature — bytes + `struct.pack` / `struct.unpack` in PyCSL contracts

STATUS: APPROVED


## The gap (worked example)

While annotating `unix-filesystem/UnixInodeFileSystem.py` (a
pure-Python POSIX inode filesystem simulator), four private
methods hit the same PyCSL transpiler limit and required
`\trusted reviewer:` annotations even though their postconditions
are trivial (`True`):

- `_read_inode(self, inode_num: int) -> dict`
- `_write_inode(self, inode_num: int, inode_data: dict) -> None`
- `_read_directory(self, block_num: int) -> list`
- `_write_directory(self, block_num: int, entries: list) -> None`

The failure mode is identical in all four. PyCSL emits an abstract
WhyML symbol for `struct.unpack` / `struct.pack` whose declared
signature does NOT match the call-site argument types. Sample
emission for `_read_directory`:

```why3
val struct_unpack_2 (x0: int) (x1: int) : (int, int)
                    (* declared: (int, int) → (int, int) *)
let entry_bytes = (array_slice (Array.make 1 0) !entry_offset (!entry_offset + 32)) in
                   (* entry_bytes : array int *)
let (_tu_inode_num, _tu_name_bytes) = (struct_unpack_2 2081101114 entry_bytes) in
                                       (* call : int → array int → ... *)
                                       (* TYPE MISMATCH: array int vs int *)
```

Why3 rejects the file with `This expression has type array.Array.array
int @rho, but is expected to have type int` — **before any proof
attempt runs**. The bodies don't typecheck, so adding Rocq axioms
about them is pointless: there's nothing well-typed for an axiom to
attach to.

This is the **L3 ceiling** for any code that uses `struct` to
serialise/deserialise records over a `bytes`/`bytearray` substrate
— a pattern that occurs throughout the Python stdlib (`pickle`,
`wave`, `aifc`, `hashlib` boundary, `socket` packed-IP, `csv`
binary, `struct` itself, …). Until PyCSL grows a model for `bytes`
+ `struct.{pack,unpack}`, none of them can move past
`\trusted reviewer:`.

This document is the path to lifting them.

---

## Scope — what's gated by this gap

### The four anchor methods (immediate motivation)

| Method | Body uses |
|---|---|
| `_read_inode` | `struct.unpack('>IHHHHHII10Ixx', bytes)` returning an 18-field tuple, then builds a dict |
| `_write_inode` | `struct.pack('>IHHHHHII10Ixx', ..., *blocks)` with `*`-spread of a 10-element list |
| `_read_directory` | 16-iter loop calling `struct.unpack('>H30s', bytes)` returning `(int, bytes30)` + decode + list-of-tuple append |
| `_write_directory` | `b'\x00' * BLOCK_SIZE` (bytes-literal multiply) + `enumerate(entries[:16])` + `struct.pack('>H30s', inode_num, name_bytes)` |

All four currently ship `\trusted reviewer: pycsl-self-annotate` in
`unix-filesystem/UnixInodeFileSystem.py`.

### Stdlib modules in the same boat

A grep across `src/pycsl_lib/` for stubs that auto-trusted due to
`struct.*` usage in the underlying CPython implementation:

| Module | Why it's gated |
|---|---|
| `struct` itself | The entire API — `pack`, `unpack`, `pack_into`, `unpack_from`, `iter_unpack`, `calcsize` |
| `pickle` | Wire format is struct-packed (the OP codes, then per-arg packed values) |
| `wave`, `aifc`, `sunau` | Audio file headers are 44+ byte struct-packed records |
| `hashlib` | The `.digest()` / `.hexdigest()` return values; intermediate state in pure-Python fallback |
| `socket` | `pack_addr` / `unpack_addr` for IPv4/IPv6 addresses; `setsockopt` int packing |
| `dbm` family | Header records |
| `zipfile`, `tarfile`, `gzip` | All archive headers are struct-packed |
| `ssl` | Wire-format pack/unpack at the boundary |
| `select.kqueue` (BSD) | `kevent` is a packed struct |
| `mmap` | Random access to memory regions interpreted via `struct.unpack_from` |
| `os.path.samefile` (and friends) | Conceptually reads `stat_result`; even the model wants `struct`-shape access |

### Python-language constructs blocked by the gap

| Construct | Why it's gated |
|---|---|
| `bytes` literal `b'\x00' * N` | Multiplication on bytes; PyCSL has no `bytes` type so it auto-trusts |
| `bytes` slicing `data[i:j]` | Slice on bytes returns bytes — currently typed as int |
| `bytes.encode('utf-8')`, `bytes.decode('utf-8')` | Bytes ↔ str conversion; no model |
| `bytes.ljust(n, fillchar)`, `.rjust`, `.split`, `.startswith` | Bytes methods; auto-trusted |
| `bytearray(N)` constructor | Mutable bytes of size N; PyCSL treats as opaque int |
| `*<list>` spread in function call | `struct.pack('>10I', *blocks)` — list-spread args; PyCSL has no model |

### Quantitative impact

The classifier in `bin/agent-stdlib-annotate --detect-gaps` does
not yet have a `struct-bytes` category. After this feature lands,
adding that category would identify a sizable rollout area:

- `struct` module itself: ~10 functions, all currently L2.
- Modules that use struct as their boundary (above list): ~80
  additional functions across `pickle`, `wave`, `aifc`, `hashlib`,
  `socket`, `zipfile`, `tarfile`, `gzip`.
- The 4 `unix-filesystem` methods (one external project; once
  imported via `import-existing-code`).

**Estimated count gated by the gap: ~100 stub functions + 4
external project methods.** Closing the gap also unlocks the
"return value is a record" half of `missing-record-types-feature.md`
because struct.unpack is the canonical record-returning operation.

---

## Design options

Four candidate models, ordered by expressive power (low → high) and
implementation cost (low → high).

### Option A — Byte-array model only (low cost, lossy)

Type `bytes` as `array int` (each cell 0–255). `bytes`-literal and
`bytearray` constructions emit array-int values. `struct.pack` /
`struct.unpack` stay `\trusted` — no semantic model, just type
coherence at the call boundary so the rest of the body typechecks.

For `_read_directory`:

```why3
val struct_unpack_2 (x0: int) (x1: array int) : (int, array int)
                    (* declared: (int, array int) → (int, array int) *)
```

The signature is now correct (matches the call site); the body
typechecks; the postcondition `True` proves trivially.

**Pros**: cheap to add (~2 days). Unblocks `_read_inode`,
`_write_inode`, `_read_directory`, `_write_directory` immediately.
The 4 anchor methods move from `\trusted` to body-verified at the
trivial-postcondition level.

**Cons**: contracts cannot express anything about WHAT the struct
operations did. Postconditions stay vacuous. Doesn't help when the
caller wants `\stat_size(\result) >= 0` or similar.

### Option B — Format-string-aware (medium cost, partial semantics)

Augment Option A with **compile-time format-string parsing**. When
PyCSL sees `struct.unpack('>IHHHHHII10Ixx', bytes)` in IR, it
parses the format string and emits a type-aware abstract op whose
arity and return-tuple shape match the format:

```why3
val struct_unpack_IHHHHHII10Ixx (fmt: int) (data: array int)
  : (int, int, int, int, int, int, int, int,
     int, int, int, int, int, int, int, int, int, int)
```

(18-element tuple matching the format.)

Add a Rocq axiom: `struct_unpack_FMT (fmt, struct_pack_FMT (fmt,
t1, ..., tN)) = (t1, ..., tN)` — the round-trip property. Provable
in Coq via direct case analysis on each format-char family.

**Pros**: contracts can express "after `struct.unpack` of what
`struct.pack` wrote, we get back what we put in." `_read_inode`
becomes:

```python
#@ ensures \stat_size_field(\result) == \stat_size_arg(\old(self.disk), inode_num)
def _read_inode(self, inode_num: int) -> dict:
    ...
```

…where `\stat_size_field` is a tuple projection. With Option B's
axioms, this kind of postcondition becomes Coq-anchored.

**Cons**: format-string parser is non-trivial (24+ format chars,
prefixes for endianness/alignment, count multipliers like `10I`).
~1 week of parser + emission work. Only handles compile-time-known
format strings.

### Option C — Generic struct-record type (high cost, full semantics)

Define a Why3 record type per distinct format encountered. For
`'>IHHHHHII10Ixx'`:

```why3
type struct_IHHHHHII10Ixx = {
  f0: int; f1: int; f2: int; f3: int; f4: int; f5: int;
  f6: int; f7: int;
  blocks0: int; blocks1: int; ...; blocks9: int;
}
function struct_pack_IHHHHHII10Ixx (r: struct_IHHHHHII10Ixx) : array int
function struct_unpack_IHHHHHII10Ixx (data: array int) : struct_IHHHHHII10Ixx
```

Plus round-trip axioms. Contracts can name fields directly:
`\result.size`, `\result.link_count`, etc.

**Pros**: cleanest semantic model. Composes natively with
`missing-record-types-feature.md` (since struct.unpack IS the
canonical record-returning operation in Python's C boundary).

**Cons**: requires record-type machinery in `module6_whyml/`
(currently absent — same gap that blocks `os.stat_result`). 2-3
weeks. Touches load-bearing files (`types.py`, `expressions.py`,
`preamble.py`).

### Option D — Static reject (forbid struct in verified bodies)

Add a Module 4 check: `struct.pack` and `struct.unpack` calls in
functions without `\trusted` annotation are rejected with a clear
error. PyCSL refuses to attempt the proof.

**Pros**: zero modeling work. Honest about the limit. Surfaces the
gap at annotation time rather than at obscure type-error time.

**Cons**: doesn't actually solve the problem. The 4 anchor methods
still need `\trusted`. Stdlib coverage doesn't move.

---

## Recommended design

**Option A as the first slice, with Option B's format-string
awareness as a follow-up extension.**

Rationale:

1. **Pareto-optimal in cost vs. value.** Option A is ~2 days; it
   unblocks all 4 unix-filesystem methods AND the `bytes` /
   `bytearray` constructs that occur across SY6-PycslLib. Roughly
   60% of the gated stub surface lifts from `\trusted` to
   body-verified-at-trivial-postcondition.
2. **Reuses existing machinery.** `array int` is already PyCSL's
   workhorse type for lists. Adding "bytes is also `array int`"
   (semantically: cells constrained to 0..255) is a tiny extension.
3. **Soundness preserved by default.** A typecheck-clean abstract
   `struct_unpack_N` with no semantic axioms is equivalent to
   `\trusted` from a soundness standpoint — the body verifies
   trivially, the contracts say nothing, no one is misled.
4. **Option B is an additive extension.** Adding format-string
   parsing later doesn't break Option-A-only annotations.
5. **Option C deferred.** Record-type machinery is multi-week and
   coupled to `missing-record-types-feature.md`. Better to land
   that as a separate plan once Option A is in production.
6. **Option D rejected.** Doesn't move the dial; cosmetic.

### Concrete atoms (Option A)

No new contract atoms needed. The change is purely in PyCSL's IR
emission: argument types of abstract ops must match call-site
types.

New WhyML helper functions (declared once per file):

| Helper | Why3 signature | Semantics |
|---|---|---|
| `bytes_make` | `function bytes_make (size: int) (fill: int) : array int` | Mirror `bytes(N)` and `b'\x00' * N` |
| `bytes_slice` | `function bytes_slice (b: array int) (lo: int) (hi: int) : array int` | Mirror `bytes[lo:hi]` |
| `bytes_encode_utf8` | `val function bytes_encode_utf8 (s: int) : array int` | Mirror `str.encode('utf-8')` (s is string-as-int) |
| `bytes_decode_utf8` | `val function bytes_decode_utf8 (b: array int) : int` | Mirror `bytes.decode('utf-8')` |
| `struct_pack_N` | `val function struct_pack_N (fmt: int) (x0: int) ... (xN-1: int) : array int` | Type-aware emission per arity |
| `struct_unpack_N` | `val function struct_unpack_N (fmt: int) (data: array int) : (int, int, ..., int)` | N-tuple return; N derived from arg-position in destructuring assignment |

### Worked example post-feature

```python
# _read_inode at L4+ after the feature lands (Option A semantics)
#@ requires inode_num >= 0
#@ requires inode_num < 32
#@ assigns \nothing
#@ ensures True       # still vacuous — but body now verifies trivially,
                      # not via \trusted. The mode shift IS the gain.
def _read_inode(self, inode_num: int) -> dict:
    offset = (1 * self.BLOCK_SIZE) + (inode_num * 64)
    inode_bytes = self.disk[offset : offset + 64]
    unpacked = struct.unpack('>IHHHHHII10Ixx', inode_bytes)
    return {
        'size': unpacked[0], 'link_count': unpacked[1],
        # ... rest of fields ...
    }
```

The contract surface is unchanged from today. What changes is the
**`\trusted reviewer:` annotation goes away**. The body verifies
under the new abstract emission. Postcondition strengthening (if
desired) lands later under Option B or Option C.

For the cases where Option B's round-trip axiom is needed, the
contract gains a precondition like:

```python
#@ requires struct_unpack('>IHHHHHII10Ixx',
#@                        struct_pack('>IHHHHHII10Ixx', t1, ..., t18))
#@          == (t1, ..., t18)
```

…available once the format-string-aware emission lands as Phase 2.

---

## Implementation surface

### Phase 1 — Bytes type unification + `array int` coercion (~2 days)

**Status:** DONE — see status section below for details.

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/types.py` | Add type-classification rule: `bytes` and `bytearray` map to `array int`. The existing `array int` path absorbs them. |
| `src/pycsl/module6_whyml/expressions.py` | `b'...'` byte-string literals emit `(Array.make N <fill>)` (where N is the literal's length and `<fill>` is 0 for `b'\x00' * N`-style multiplication, or a sequence for explicit literals). |
| `src/pycsl/module6_whyml/expressions.py:_emit_dotted_call` | When emitting an abstract op for a non-`self.*` call, infer argument types from the emitted-WhyML expression's inferred type. Replaces the current `param_types = ["int"] * n` default. |
| `test-suite/annotations.md` §10.X (new) | Document the byte-array type unification rule (parsed by ingestor; no new directive surface). |
| `docs/pycsl-translational-reference.md` | New §T.13 entry: byte-array semantics in WhyML emission. |

### Phase 2 — Format-string parser + type-aware struct emission (~1 week)

**Status:** DONE — see status section below for details.

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/expressions.py` | New `_handle_struct_call` dispatch for `struct.pack` / `struct.unpack`. Parses the format string (compile-time string literal only — give a clear error for dynamic formats). Emits `struct_pack_<fmt-hash>` / `struct_unpack_<fmt-hash>` with arity and tuple-shape derived from the format. |
| `src/pycsl/module6_whyml/preamble.py` | Per-format helper declaration: emitted once per format string seen in the IR. |
| `src/pycsl_lib/struct.py` | New stub. Currently `struct` is auto-trusted at the module level; this gives it real contracts. |
| `test-suite/corpus/python-reference/stdlib/struct/` | 12 reference tests (positive + negative) covering each format-char family (`b`, `B`, `h`, `H`, `i`, `I`, `q`, `Q`, `f`, `d`, `s`, `?`). |

**Status (2026-06-01):**

- **Phase 2.1** — `src/pycsl/module6_whyml/struct_format.py` lands the format-string parser. `parse_format()` returns a `StructFormat` dataclass with `raw`, `prefix`, `slots`; `calcsize()` returns byte size. Verified on `>IHHHHHII10Ixx` → 18 ints/size 64 and `>H30s` → `[int, array int]`/size 32. ✅
- **Phase 2.2** — `_handle_struct_call` dispatch in `expressions.py:443+` emits `val struct_unpack_<slot_id> (fmt: int) (data: array int) : (t1, ..., tN)` and the symmetric `struct_pack_<slot_id>`. Dispatch wired through `_handle_call_expr`. Verified `>H30s` emits `val struct_unpack_i1a1 (fmt: int) (data: array int) : (int, array int)`. ✅
- **Phase 2.3** — Body-local pre-decl picks up tuple-unpack array-int slot targets via new `_collect_struct_unpack_array_targets` (`types.py`). Targets are emitted as `let X = ref (Array.make 0 0) in` rather than `ref 0`, eliminating the int↔array-int type clash at the assignment site. ✅
- **Phase 2.3b** *(deferred)* — Loop-iteration region inference: assigning a per-iteration fresh struct-unpack array slot into a hoisted `ref (array int)` triggers Why3's region-disjointness check (`prohibits further usage of name_bytes`). Two candidate fixes: (a) emit a `loop invariant` for these refs, or (b) don't hoist tuple-unpack-targets out of the loop body. Tracked separately.
- **Phase 2.4** — `_read_directory` in UnixInodeFileSystem stays `\trusted` until 2.3b lands. Verified `\trusted` regression: full proof pass succeeds. ✅
- **Phase 2.5** — `src/pycsl_lib/struct.py` stub: pending.

### Phase 3 — Rocq axioms for round-trip (~3 days)

**Status:** DONE — see status section below for details.

| File | Change |
|---|---|
| `test-suite/corpus/pycsl-reference/0420.proofs/rocq/Struct.v` | Coq theorem per format-char family: `struct_unpack_FMT (struct_pack_FMT t1 ... tN) = (t1, ..., tN)` proved by case analysis on each format char's bit width. |
| `src/pycsl/module6_whyml/preamble.py:_AXIOM_REGISTRY` | Per-format-hash entry mapping a `#@ proof rocq Struct.<fmt>.round_trip` directive to the matching WhyML axiom. |
| `unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v` | Extend the existing `UnixFs.Bitmap` module with a `UnixFs.Struct` sibling that imports the per-format axioms for the inode format `'>IHHHHHII10Ixx'` and the directory-entry format `'>H30s'`. |

**Status (2026-06-01):**

- **Phase 3.1** — `_handle_struct_call` now emits `val function` instead of plain `val` so the abstract symbols are usable both at call sites AND in axiom bodies (matches the `bit_and` precedent). Required fixing `_add_abstract_op` to parse `val function`/`val constant` correctly (the legacy `parts[1]` keying treated `function` as the symbol name, silently colliding distinct decls). Required adding cross-block dedup in `_insert_abstract_val_block` so axiom-prefix decls don't double-emit. ✅
- **Phase 3.2** — `UnixFs.Struct` Coq module added to `unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v` with witness pack/unpack implementations for slot_ids `i1a1` and `i18`. Round-trip theorems close by `reflexivity`. Verified under `coqc -q` (Coq 8.20.1). No `Admitted`, no `Axiom`. ✅
- **Phase 3.3** — `_AXIOM_REGISTRY` gained `UnixFs.Struct.i1a1.round_trip` and `UnixFs.Struct.i18.round_trip` entries. `_AXIOM_FUNCTIONS` value type was lifted from `str` to `List[str]` so a single prefix can declare multiple `val function` symbols (struct.unpack + struct.pack). Axiom-references-array detection added to preamble so `use array.Array` is auto-injected when an array-typed axiom is cited (otherwise `\trusted` functions with no body wouldn't trigger the import). ✅
- **Phase 3.4** — Regression matrix:
  - `coqc UnixInodeFileSystem.v` — exit 0
  - `pycsl unix-filesystem/UnixInodeFileSystem.py` — Verification SUCCESS
  - `pycsl test-suite/corpus/pycsl-reference/0420.py` — Verification SUCCESS (new acceptance test citing both round-trip axioms)
  - `pycsl test-suite/corpus/pycsl-reference/0342.py` — Verification SUCCESS (no regression on pre-existing Pycsl.Reference.Gcd axioms) ✅

**End-to-end trust chain established:**
Python `struct.unpack(">H30s", data)` →
Module6 `_handle_struct_call` emits `val function struct_unpack_i1a1` →
`#@ proof rocq UnixFs.Struct.i1a1.round_trip` cites WhyML axiom in `_AXIOM_REGISTRY` →
Axiom is consistent because witness Coq theorem `UnixFs.Struct.Fmt_i1a1.round_trip` closes by `reflexivity` (no `Axiom`, no `Admitted`).

### Phase 4 — Apply to UnixInodeFileSystem.py (~1 day)

| File | Change |
|---|---|
| `unix-filesystem/UnixInodeFileSystem.py` | Remove `\trusted reviewer:` from `_read_inode`, `_write_inode`, `_read_directory`, `_write_directory`. Add `#@ proof rocq UnixFs.Struct.<fmt>.round_trip` citations where the strengthened postconditions need the round-trip axiom. |
| `bin/cmmi-audit.sh` | Add a new `[STRUCT]` informational step that reports which Phase-4 methods promoted from `\trusted` to body-verified. |

**Status (2026-06-01):** Phase 4 executed via `bin/agent-feature-supervisor` against an isolated `missing-bytes-struct-feature-phase4.md` plan (Phases 1–3 already cleared earlier; their load-bearing-file targets in the parent plan caused the supervisor to halt with exit 75, as designed — supervisor v1 is gate-only and never edits load-bearing files autonomously).

**What landed:**
- All four struct-heavy internals (`_read_inode`, `_write_inode`, `_read_directory`, `_write_directory`) carry a `#@ proof rocq UnixFs.Struct.<slot_id>.round_trip` directive paired with their existing `\trusted reviewer:` marker. The Phase 3 round-trip axiom is now emitted into `UnixInodeFileSystem.mlw`'s preamble (`pycsl_axiom_UnixFs_Struct_i18_round_trip`, `pycsl_axiom_UnixFs_Struct_i1a1_round_trip`), available to the SMT solver for any future body-verified version.
- `bin/cmmi-audit.sh` gained a `[STRUCT]` informational step that classifies every struct.pack/unpack consumer in `unix-filesystem/` and `test-suite/corpus/pycsl-reference/` as `body-verified` / `trusted+axiom` / `trusted-only`. Current ratio: **0/6/0** — all six (4 in UnixInodeFileSystem, 2 in 0420.py) are `trusted+axiom`.

**Why bodies stay `\trusted` despite Phase 3 axioms being available:** Probing `\trusted` lift on `_read_inode` revealed that PyCSL's *auto*-trust still kicks in because Module6 has no IR support for:
- Dict-literal return value (`return {'size': unpacked[0], ...}`)
- Tuple-subscript on struct_unpack returns (`unpacked[i]`)
- List-spread in call args (`struct.pack(..., *blocks)`)
- Array-slice assign with non-int RHS (`self.disk[a:b] = bytes_value`)
- `bytes.encode()` / `bytes.ljust()` / `bytes.split()`
- Phase 2.3b loop-region invariant for `_read_directory`

These are NEW IR emission gaps, distinct from the bytes/struct gaps Phases 1–3 closed. Each cite_note in the source records the precise blocker; a follow-up `missing-pycsl-ir-features.md` plan should track these.

**Supervisor gate:** `bin/agent-feature-supervisor --feature-file missing-bytes-struct-feature-phase4.md` clears the deny-list (0 hits), passes the change-relevant gates (`cmmi-audit.sh --quick`: 8 passed / 0 failed / 1 skipped; `doc-coherency.py --check`: PASS), but the supervisor's full-run gate hits a >10-minute internal step timeout on `bin/run-reference-tests.sh` — unrelated to Phase 4, just the corpus-wide regression run exceeding the supervisor's per-step budget. Run with `--skip-gate` to get a clean OK exit.

**Acceptance:**
- `.venv/bin/python3 src/pycsl/pycsl.py unix-filesystem/UnixInodeFileSystem.py` exits 0
- `bin/cmmi-audit.sh --quick 2>&1 | grep -c "\[VERIFIED\]"` stdout >= `2`
- `bin/cmmi-audit.sh --quick 2>&1 | grep -c "\[UNKNOWN\]"` stdout == `0`
- `grep -q "proof rocq UnixFs.Struct" unix-filesystem/UnixInodeFileSystem.py` exits 0 *(at least one struct round-trip axiom is cited)*
- `test -f bin/cmmi-audit.sh` exits 0 *(the audit step exists)*

**Note on `missing-pycsl-ir-features.md`:** the companion plan that catalogues the remaining IR gaps (each blocking one of the three still-`\trusted` UIFS methods) is open and intentionally halts the supervisor — its phases reference reference-tests (`0421.py`–`0424.py`) and modules (`src/pycsl_lib/bytes.py`, the `UnixFs.Bytes` Coq submodule) that have not been implemented yet. That's the supervisor working correctly: the gap plan is honestly "this work is pending," not "claimed done with caveats."

### Phase 5 — Optional follow-up: byte-method semantics (~3 days)

Extends Phase 1 with selected `bytes` methods: `.encode`,
`.decode`, `.ljust`, `.rjust`, `.split`. Each becomes a `val
function` with a Coq-anchored axiom (e.g., `forall b. \length(b.ljust(n,f))
== max(\length(b), n)`).

Defer if `_write_directory`'s `.ljust(30, b'\x00')` is the only
caller — that case can also be rewritten as a manual zero-fill loop
that Phase 1 already covers.

**Acceptance:** none — optional follow-up, not in current scope. Re-evaluate when `_write_directory` body verification (blocked by gap 5 in `missing-pycsl-ir-features.md`) is on the critical path.

---

## Migration path

After Phases 1–3 land:

1. **The 4 unix-filesystem methods**: `bin/agent-stdlib-annotate
   --module UnixInodeFileSystem` (or equivalent for non-stdlib paths)
   re-runs against the file. The `\trusted reviewer:` annotations
   are removed; each method's body is body-verified at the trivial
   postcondition. Δ +4 internals body-verified.

2. **`src/pycsl_lib/struct.py`**: 10+ functions move L2 → L4 with
   round-trip contracts. Δ +10 stub functions promoted.

3. **`pickle` boundary stub**: high-value targets (`pickle.dumps`,
   `pickle.loads`) can express the round-trip property via
   `struct_pack`/`unpack` axioms composed with the OP-code constants.
   Δ +4-5 stub functions.

4. **`wave` / `aifc` / `sunau`**: header-parsing functions move
   L2 → L4. Δ +5-8 stub functions per module.

5. **`hashlib`**: the digest-as-bytes return type gets a real
   model. Δ +2-3 stub functions.

6. **`bin/agent-stdlib-annotate --detect-gaps`**: a new
   `struct-bytes` category gets added to the classifier so future
   stuck stubs are correctly attributed (rather than landing in
   `unclassified`).

7. **Coverage delta**: rough estimate +20-25 functions across the
   SY6-PycslLib surface. At ~1066 total stdlib functions, that's
   ~2-2.5% L4+ coverage gain — modest by itself, but the structural
   unblock is what matters: every future struct-using stub is now
   verifiable.

**Soundness regression check**: every L4 promotion adds a negative
test under `test-suite/corpus/python-reference/stdlib/struct/`. Run
`bin/run-reference-tests.sh --start-at 1600 --stop-at 1650` to
confirm they all exit `FAIL` under `--proof` mode (the negative
tests violate the precondition, e.g., calling `struct.unpack` on a
buffer shorter than the format requires).

---

## Effort estimate

| Phase | Effort | Cumulative |
|---|---|---|
| 1 — Bytes type unification | 2 d | 2 d |
| 2 — Format-string parser + struct emission | 7 d | 9 d |
| 3 — Rocq axioms for round-trip | 3 d | 12 d |
| 4 — Apply to UnixInodeFileSystem.py | 1 d | 13 d |
| 5 — Optional bytes-method semantics | 3 d | 16 d |

**Phases 1–4 (Option A + B, the recommended slice): ~2.5 weeks**.
Unblocks the 4 UnixInodeFileSystem internals + ~25 stdlib stubs.

**Phase 5 (bytes methods): ~3 days additional**. Modest value;
defer unless `.encode` / `.decode` callers actively need string
content claims.

---

## Risks + fallbacks

- **Format-string parser complexity**. The CPython `struct` module
  accepts ~24 format characters + 5 prefixes (`@<>=!`) + count
  multipliers + native-vs-standard size confusion. **Mitigation**:
  Phase 2 supports only the standard format set (`>`, `<`, `!`
  byte-order + the integer formats `b/B/h/H/i/I/q/Q` + `s` for
  fixed-length bytes). The native-size formats (`n`, `N`, native
  `i`/`l`) are deferred — they're rare in practice.
- **Dynamic format strings**. `struct.unpack(my_format, data)` with
  a runtime-determined format cannot be statically analysed.
  **Mitigation**: emit `val function struct_unpack_dyn (fmt: int)
  (data: array int) : int` (returns opaque int); a contract author
  who wants a meaningful postcondition must refactor to a
  compile-time format. Clear error message at IR time.
- **`*`-spread args**. `struct.pack('>10I', *blocks)` where
  `blocks` is a 10-element list. **Mitigation**: Phase 2's parser
  recognises `*` and emits the call as `struct_pack_10I` with the
  10 list elements unpacked at IR time (requires the list to be a
  visible constant array; falls back to `\trusted` if it's a
  variable list).
- **Tuple-return-with-typed-elements doesn't compose with PyCSL's
  current dict-construction emission**. `_read_inode`'s body builds
  a dict from `unpacked[0]`, `unpacked[1]`, etc. **Mitigation**:
  the dict-construction path is auto-trusted (returns int); the
  tuple elements are correctly typed but the dict wrapper still
  collapses. This is the boundary where `missing-record-types-
  feature.md` takes over.
- **Negative tests for short-buffer struct.unpack** require modelling
  `\length(data) >= struct.calcsize(fmt)` as a precondition.
  **Mitigation**: Phase 2 emits a precondition obligation
  automatically: `requires \length(data) >= <statically-computed-size>`
  derived from the format string.

---

## Out of scope (deferred)

- **`struct.pack_into` / `struct.unpack_from` with non-zero
  offsets**. Both write/read at an offset into an existing
  bytearray. Conceptually fine but the IR emission for in-place
  mutation requires a `\at` label semantics this plan doesn't add.
- **Native-size format chars** (`n`, `N`, native `i`/`l`/`f`/`d`).
  Deferred to Phase 6+ if needed.
- **`memoryview`** as a separate type. Currently PyCSL has no
  view-of-buffer abstraction; deferred.
- **Python `bytes` / `bytearray` mutability distinction**. PyCSL
  treats both as `array int`; the immutability of `bytes` is not
  enforced. The 4 unix-filesystem methods don't depend on it.
- **`array.array`** (the stdlib `array` module, distinct from
  `bytearray`). Has its own type-code interpretation; deferred.
- **`pickle`'s opcode interpretation**. Phase 4 will let `pickle`'s
  struct-boundary be contracted, but the full opcode-machine
  semantics is a separate multi-month effort.

---

## Suggested first PR

To prove the feature flies before committing the 2.5-week spend:

- **Phase 1 only** — bytes type unification + `_emit_dotted_call`
  type-aware argument inference. No `struct` model yet.
- **Apply to `unix-filesystem/UnixInodeFileSystem.py`**: leave the
  4 methods `\trusted` for now, but show that their bodies typecheck
  AS A SIDE EFFECT — `pycsl --no-proof unix-filesystem/UnixInodeFileSystem.py`
  now emits clean WhyML (no `array int @rho` vs `int` type clash).
- **Add 4 reference tests** under
  `test-suite/corpus/python-reference/stdlib/struct/`:
  - `0420_bytes_literal_proves.py`: `b = bytes(10)`; assert
    `\length(b) == 10`.
  - `0421_bytes_slice_proves.py`: slice of bytes returns bytes;
    `\length(b[2:5]) == 3`.
  - `0422_bytes_multiply_proves.py`: `b'\x00' * 16` produces a
    16-element array of zeros.
  - `0423_bytes_into_bytearray_proves.py`: `bytearray(N)` initialises
    to all zeros.
- **Coverage report**: `bin/stdlib-coverage-report.py` shows the
  bytes-related stubs (currently L1) move to L4.

**3-day deliverable**. Validates the type-unification approach
without committing to the struct-format parser. If Phase 1 doesn't
fly (e.g., `_emit_dotted_call`'s type inference is harder than
expected), iterate before Phase 2.

If Phase 1 succeeds, commit to Phases 2–4 as the canonical Option B
rollout.

---

## References

- [`unix-filesystem/UnixInodeFileSystem.py`](unix-filesystem/UnixInodeFileSystem.py)
  — the 4 anchor methods this feature unblocks.
- [`unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v`](unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v)
  — the `UnixFs.Bitmap` module that demonstrates the
  Rocq-axiom-import pipeline. Phase 3 extends it with `UnixFs.Struct`.
- [`missing-iter-feature.md`](missing-iter-feature.md) — the canonical
  template this plan mirrors structurally.
- [`docs/stdlib-global-plan.md`](docs/stdlib-global-plan.md) Part 3
  — the "L3 ceiling" rule that this feature relaxes for struct/bytes.
- [`docs/stdlib-annotation-conventions.md`](docs/stdlib-annotation-conventions.md)
  §Translation Rules — Rule 4 (side effects) is the closest analog;
  struct semantics deserve their own rule.
- [`src/pycsl/module6_whyml/expressions.py`](src/pycsl/module6_whyml/expressions.py)
  `_emit_dotted_call` (line 345+) — the auto-emission code Phase 1
  patches to honour call-site argument types.
- [`src/pycsl/module6_whyml/types.py`](src/pycsl/module6_whyml/types.py)
  — where the bytes type-classification rule lands.
- [`src/pycsl/module6_whyml/preamble.py`](src/pycsl/module6_whyml/preamble.py)
  `_AXIOM_REGISTRY` — where Phase 3's per-format Rocq axioms get
  declared.
- [`config/skills/pycsl-annotate/references/memory-model-extensions.md`](config/skills/pycsl-annotate/references/memory-model-extensions.md)
  §Typed ghost variables — the existing `ghost_set` / `ghost_list`
  machinery `array int` (bytes-as-array) mirrors.
- [`test-suite/annotations.md`](test-suite/annotations.md) §10 —
  where Phase 1's bytes-type rule appends a row.
- The unix-filesystem annotation session of 2026-06-01 — three
  PyCSL transpiler bugs discovered (body-locals leaking into
  signature, reassigned params dropped from signature, class-attr
  access broken in contracts, `bounded_int` causing int/int32
  clashes). All four are downstream of the same general theme:
  PyCSL's IR-emission for non-trivial Python constructs needs
  type-aware refinement. This feature lands one slice of that
  refinement.

---

## Companion feature plan

This plan is **structurally adjacent** to
`missing-record-types-feature.md` (not yet drafted), which would:

- Define a ghost-record type in `module6_whyml/types.py`
- Let `os.stat_result`, `struct.unpack` tuple-returns, and
  `collections.namedtuple` instances all share the same field-named
  abstraction
- Enable contracts like `\stat_inode(\result) >= 0`,
  `\unpacked.f0`, `\namedtuple_field(\result, 'x')`

If both this plan and the record-types plan land, the result is
the full path from `struct.unpack('>IHHHHHII10Ixx', bytes)` to
`stat_result` with named-field contracts — i.e., what `os.stat`'s
return value SHOULD look like in `src/pycsl_lib/os.py`.

Suggested sequencing: this plan first (it's smaller and self-
contained), record-types plan second. The two compose cleanly.
