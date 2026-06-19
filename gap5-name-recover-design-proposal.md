# Gap-5 design proposal — the faithful byte→str RECOVER (read-direction name codec)

**Status:** DESIGN ONLY (no production code change). Read-only experiments run in
`/tmp` and cleaned; tree clean except this file.
**Date:** 2026-06-19
**Author scope:** under the **no-more-int doctrine** ([[feedback_no_more_int]]) and
the extreme-rigor doctrine (`test-supervise-sl.md` §Doctrine).

---

## 0. RECOMMENDATION + EFFORT (read this first)

**RECOMMENDATION: SPIKE FIRST (os-name-only, design option (a) — "eliminate the leak
at source"), then decide on the general rollout.** Do **not** start the general
string-lowering refactor blind.

- The faithful fix is **option (a): stop hashing the read name; lower it to the SAME
  `field_to_str(self.dir, off, 30)` logic symbol the encode side and `slot_name`
  already use.** This is the *only* doctrine-aligned option and — critically — it
  needs **NO new axiom**: the bridge `slot_name d blk k = field_to_str d (blk*512+32*k+2)
  30` is **already landed and cross-validated** (`UnixFs.Dir.slot_name_byte_decode`,
  `0712.proofs/`). So `slot_name == pathname` would reduce to a string equality the
  EXISTING decode axioms discharge. The soundness cost of (a) is **zero new TCB**.
- **Effort: the SPIKE is S–M; the general rollout is L–XL.** The os-name-only spike
  (make just the dir-entry read name faithful, re-run the Milestone-0 value-marker
  spike's `slot_name==pathname` branch in the full gate ×2) is small *code* but the
  decisive risk is whether the full-gate explosion (Milestone-0's A.7 wall) clears —
  that is a measurement, not a build. The **general** elimination of the int-hash
  fallback across all `decode`/`split`/string-literal sites is L–XL and **NOT
  corpus-inert** (it changes string lowering for any module with bytes/string flow).
- **Biggest risk:** the spike is cheap to *try* and the upside is large (unblocks the
  read-side dirscan trio `\trusted` 4→1 and likely fd-resolution), BUT there is a real
  chance that even a faithful disk-byte-dependent name **still** doesn't bridge cleanly
  in the FULL body gate — because Milestone-0 already proved the value-marker half hits
  an A.7 aggregate-context explosion one layer up. Gap-5 is *necessary* for the read
  side; the spike tells us if it is *sufficient*. **Spend the spike; gate the L–XL
  rollout on the spike's full-gate verdict.**

---

## 1. PROBLEM STATEMENT & SCOPE

### 1.1 The wall (cited, not re-derived)

The read-side Milestone-0 spike returned a clean **NO**
(`getting-better/20260619-2230-dir-lookup-milestone0-NO.md`). Its §5 isolates the
obstruction syntactically from the emitted `_dir_lookup` body:

```
name := (decode_1 1501791143);                  (* OPAQUE INT HASH — zero disk-byte dependence *)
... guard: !name = str_hash_op pathname ...      (* int-hash compare, NOT slot_name *)
assert { dir_scan_prefix self.dir 5 pathname (!i+1) ... }  (* Timeout — step branch undecidable *)
```

The marker INTRO step needs the branch condition `slot_name(self.dir, 5, i) ==
pathname`, where `slot_name` is a real WhyML **`string`**. The body's per-slot `name`
is the **opaque int hash** `decode_1 1501791143 : int`, with **zero dependence on
`self.dir` bytes** and **not even the same WhyML type** as `slot_name`. The recover
assert is not type-compatible (`slot_name : string` vs `name : int`). The marker step
can never be selected, the prefix invariant cannot advance, and the goal explodes
(Milestone-0 §3: 4 non-Valid on `_dir_lookup`, multi-million steps, ×2 deterministic).

### 1.2 The source of the leak (reproduced this run, file:line)

I reproduced the exact lowering from the read body shape (read-only `/tmp` probe,
cleaned). The leak is in `src/pycsl/module6_whyml/`:

- **`stable_hash`** (`identifiers.py:8-16`): "the legacy opaque-string→int fallback" —
  `sha256(s)[:8] % 2147483647`. Deterministic int with **zero structural relation to
  any string semantics**.

- **`_str_operand_to_int`** (`expressions.py:402-412`): when a string is compared
  against an int (the inlined `_dir_lookup` `name == pathname` shape), `pathname` →
  `str_hash_op pathname : int` and a literal → `stable_hash`. This produces the
  `!name = str_hash_op pathname` guard.

- **`decode` lowering** (`expressions.py:1276-1285`): two modes.
  - default (int model): `decode_1 <int> : int` — the `decode_1 1501791143` in the NO.
  - `_decode_to_string` (str-typed target, `statements.py:101-111`): `decode_str_1
    <int> : string`. **This is a `string` — but its argument is STILL the int hash**
    (`_coerce_to_int` at `expressions.py:1284`). I confirmed: with `name: str`
    annotation the body emits `let name = ref (decode_str_1 1501791143)` and
    `str_eq_op !name pathname` — a `string`, but with **zero `self.dir` dependence**.
    *The "fix it to a string" half is already half-built and STILL leaks the bytes.*

- **The chain breaks one step EARLIER, at `.split()`** (the genuinely surprising
  finding). The body is `name = name_bytes.split(b'\x00')[0].decode(...)`. I probed
  the intermediate: `name_bytes = bytes(data[2:32])` lowers FAITHFULLY to `bytes_new
  (Array.sub data 2 30) : array int` — the disk bytes are still present. But
  `name_bytes.split(b'\x00')` hits the **generic unannotated-call path**
  (`expressions.py:1308-1317`): the array receiver is `_coerce_to_int`'d to `(Array.make
  1 0)` and the call becomes `nb_split_1 (Array.make 1 0) : int`. **`split` DISCARDS
  `name_bytes` entirely** and returns an opaque int; `decode` then hashes that. So the
  read name is `decode(split(bytes)) = decode_1(hash(literal))` — three opaque hops, the
  disk bytes thrown away at the FIRST (`split`).

### 1.3 Where the int-hash fallback fires on read paths (blast-radius enumeration)

`stable_hash` callers (grep, this run): `expressions.py` ×6
(`_coerce_str_arg`:83, `_coerce_to_int`:163,181, `_str_operand_to_int`:410,
`_handle_dotted_call`-ish:2266) and `statements.py` ×2 (722, 752). These are NOT
os-specific — they are the **general str-modeling leak**: any string literal passed to
an abstract op, any tuple, any `decode`/`split`/string compared to an int.

- **On the os read path specifically:** `_dir_lookup` (`UnixInodeFileSystem.py:973`),
  `_dir_find_slot` (:1025), `_dir_find_free` (:~1054), and the helper `_unpack_direntry`
  (:425) + `_read_directory` (:923) all share the identical body line `name =
  name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')` (:983, :1035, …). All
  read names leak via `split`→`decode`→hash.
- **Broader corpus:** 12 corpus reference modules and pure_lib (`strmod`, `json`,
  `os/path`) touch `.split`/`.decode`; 661 corpus modules carry string literals (the
  `stable_hash` literal path). So the fallback is **pervasive**, not a local os bug.

**Scope conclusion:** Gap-5 is a **general str-modeling leak** that happens to be
*fatal* on the os read path. The doctrine-faithful fix is general; the *demand* (and
the safe minimal spike) is os-name-only.

---

## 2. CURRENT MODELING ANALYSIS

### 2.1 The faithful ENCODE side (already landed, cross-validated)

The write direction lowers a name to disk bytes faithfully and proves the round-trip:

- `field_to_str (d: array int) (off: int) (width: int) : string` — a pure logic
  **`function`** (`preamble.py:1132`), the `'>Ns'` null-padded byte-field → string
  codec. It is usable in **program body position** (it is a `function`, not a `val`).
- `UnixFs.Field.field_to_str_round_trip` (`preamble.py:942-950`, proofs in `0708`/`0712`):
  bytes written from `name` ⟹ `field_to_str d off width = name`.
- `UnixFs.Field.field_to_str_frame` (`preamble.py:986-991`): disjoint-region byte
  agreement ⟹ `field_to_str` equal (the slot-locality frame).
- `UnixFs.Dir.slot_name_byte_decode` (`preamble.py:324`, `0712.proofs/`): **the
  keystone bridge** — `slot_name disk blk k = field_to_str disk (blk*512+32*k+2) 30`.
  Rocq "Closed under the global context"; Lean ⊆ {propext, Quot.sound}.

These are the SAME symbols the marker/value machinery wants: `slot_name(self.dir, 5, i)
== pathname`. The encode side is sound and complete; the gap is purely the read
direction.

### 2.2 The int-hash RECOVER fallback — when/why PyCSL falls back

PyCSL falls back to the hash because **the read body never reconstructs a
disk-byte-dependent string**. Two compounding causes (§1.2):

1. **`split` is unmodeled** (`expressions.py:1308-1317` generic path): it coerces its
   `array int` receiver to a `(Array.make 1 0)` placeholder and returns `int`. The
   disk bytes are discarded at the split, before decode is even reached.
2. **`decode` (even in string mode) hashes its argument** (`expressions.py:1284`
   `_coerce_to_int`): the decode result type can be `string`, but its content is
   `decode_str_1 <hash>` — a fresh opaque string with no axiom relating it to the input
   bytes. There is **no axiom DEFINING `decode_1`/`decode_str_1` over the bytes** — by
   design, the byte→str content was "Gap 5, unmodeled" (`UnixInodeFileSystem.py:957-959`).

So the recover is "impossible today" not because a lemma is missing, but because the
read body **emits a symbol with no logical connection to the disk bytes** — there is
nothing for a lemma to bridge *to*.

### 2.3 What a faithful read-direction name would be

A WhyML **`string`** computed as **`field_to_str(self.dir, entry_offset+2, 30)`** —
the EXACT same logic symbol `slot_name_byte_decode` already equates `slot_name` to.
Then the read name *depends on `self.dir` bytes by construction*, and
`name == pathname` is a `string` equality on the same term family the marker branch
needs. **No new symbol, no new axiom** — the read body simply names the codec the
encode side already proved.

---

## 3. THE DESIGN

### Option (a) — Eliminate the leak at source (RECOMMENDED, no-more-int aligned)

Make the read body lower the per-slot name to `field_to_str(self.dir, entry_offset+2,
30) : string` — the same symbol the encode side and `slot_name` use — instead of
`decode(split(bytes))`.

Concretely there are two sub-routes to *emit* that term:

- **(a1) Special-case the `name_bytes.split(b'\x00')[0].decode(...)` idiom** in the
  emitter (Module 6) to recognize the dir-entry name-read pattern (a fixed-width
  null-terminated field of a known `array int` at a known offset) and lower it directly
  to `field_to_str(<arr>, <off>, <width>)`. Narrow, os-shaped; lowest blast radius.
- **(a2) Faithfully model `bytes.split`/`bytes.decode` over `array int`** so the
  byte chain survives: `split` keeps its `array int` receiver (return the prefix
  sub-array up to the separator), and `decode` over an `array int` lowers to
  `field_to_str` (or a `bytes_to_str` codec equated to it). General; higher blast
  radius; the true no-more-int fix.

**Does it discharge `slot_name == pathname`?** Yes, *modulo the A.7 wall*. With the
read name = `field_to_str(self.dir, off, 30)`, the branch condition `name == pathname`
plus `slot_name_byte_decode` (`slot_name = field_to_str` at this off) gives
`slot_name(self.dir, 5, i) == pathname` by transitivity — a one-step string rewrite,
**no new axiom**. This is exactly the bridge Milestone-0 §5 said was missing. The
**open question the spike must answer**: whether that bridge fires in the FULL body
gate or hits the same A.7 aggregate-context explosion the value-marker half hit
(Milestone-0 §3) — i.e. whether Gap-5 is *sufficient* as well as *necessary*.

- **Soundness:** zero new TCB. The bridge is already cross-validated (`0712.proofs/`).
  (a) merely stops emitting a symbol that *fabricated* a name and starts emitting the
  *correct* one. The value-marker axiom of the Milestone-0 spike (`0720.proofs/`,
  cross-validated) plugs in directly once the name is faithful.
- **Blast radius:** (a1) os-only, near-inert. (a2) general — changes string lowering
  for every `.split`/`.decode`/bytes-flow module (§5). NOT corpus-inert.
- **Effort:** (a1) S–M. (a2) L–XL.
- **no-more-int alignment:** PERFECT — this is the doctrine's "fix the int leak at
  source / lower each type to its faithful WhyML class" verbatim.

### Option (b) — A `str_to_field`/recover LEMMA bridging the hash to `field_to_str`

Keep the int hash; add a cross-validated axiom relating `decode_1 <hash>` (or
`decode_str_1`) to `field_to_str`.

- **Does it discharge?** No — and it is **DISQUALIFIED**. The hash `decode_1
  1501791143` depends on a string *literal* (`b'\x00'`), NOT on `self.dir`. There is no
  true theorem "`decode_1 (hash X) = field_to_str d off w`" — it is simply false (the
  LHS ignores `d`). Any axiom asserting it would be **unsound** and so could not be
  cross-validated (it would surface as a bare `Axiom` over an abstract symbol with no
  model — the exact REJECT shape in `pycsl-monitoring` A.10). The extreme-rigor
  doctrine strikes it from the option set.
- **Verdict:** REJECT. (b) cannot be made sound because the hash discards the bytes; a
  bridge needs something byte-dependent on both sides, which only (a) provides.

### Option (c) — Broader string-class refactor

Option (a2) IS the broader refactor (model `bytes`/`str` codecs faithfully so the
int-hash fallback retires generally). Treat (c) = (a2). It is the eventual no-more-int
endpoint but should be **gated on the (a1) spike** — there is no reason to pay L–XL if
the os spike reveals the A.7 wall is still fatal (then Gap-5 alone doesn't unblock the
read side and the priority shifts to the aggregate-context / module-scope problem).

**Design verdict:** pursue **(a1) as the spike**; promote to **(a2)** for the general
rollout only if the spike's full-gate verdict is YES.

---

## 4. SOUNDNESS & CROSS-VALIDATION

The decisive soundness fact: **option (a) requires NO new lemma.** What must hold for
`slot_name(self.dir, 5, i) == pathname` to discharge is the composition:

```
read name  =  field_to_str(self.dir, off, 30)      [emission change — (a), not a proof]
slot_name(self.dir, 5, i) = field_to_str(self.dir, off, 30)   [slot_name_byte_decode — LANDED, 0712.proofs]
name == pathname   (branch condition)              [program guard]
⟹  slot_name(self.dir, 5, i) == pathname           [transitivity, SMT]
```

Every proof rung is **already cross-validated zero-TCB**:
`UnixFs.Dir.slot_name_byte_decode` (Rocq "Closed under the global context", Lean
{propext, Quot.sound}; `0712.proofs/{rocq,lean}/SlotNameByteDecode.{v,lean}`), composing
with `field_to_str_round_trip`/`field_to_str_frame` (`0708`/`0714.proofs/`). The
read-side value marker (`dir_scan_result_value` + prefix rungs) is also already
cross-validated (`0720.proofs/`, banked in `SPIKE-dir-lookup-value.patch`).

So **(a) introduces no axiom that needs cross-validation** — it is an *emission* change
that lets the existing cross-validated axioms apply. This is the strongest possible
soundness posture: the fix shrinks (does not grow) the trusted base, and the
distinguishing property the read name needs (disk-byte dependence) is supplied by a
landed theorem, not a new assumption.

The only residual that could need *new* offline work is whatever the spike's full gate
surfaces (e.g. a folded read-side invariant atom if A.7 reappears) — that would be a
new human-gated cross-validated axiom, identified only after the spike measures it.

---

## 5. BLAST RADIUS / CORPUS INERTNESS & REGRESSION

### 5.1 Quantification (measured this run)

- `.expected.mlw` conformance fixtures: **38 total; 0 reference** `decode_`/`str_hash_op`
  /`str_eq_op`/`_split_`. So the **deliberate byte-diff FIXTURES are NOT directly
  affected** by a string-lowering change.
- The byte-diff sweep (`bin/byte-diff-sweep.sh`) runs over **670 corpus reference
  `0*.py` modules** (full emission, not just fixtures). **12 corpus modules** touch
  `.split`/`.decode`/`str_eq`; **661** carry string literals (the broad `stable_hash`
  literal path).
- pure_lib affected by `.split`/`.decode`: `os` (`UnixInodeFileSystem.py`, `__init__.py`,
  `path.py`), `strmod`, `json` (`__init__.py`, `_api.py`).

### 5.2 Inertness verdict by option

- **(a1) os-name-only special-case:** near-inert. Only the dir-entry name-read idiom in
  os changes emission; the 12 generic `.split`/`.decode` corpus modules keep their int
  model. Re-bless is bounded to os `.mlw` (which are validation output, gitignored).
  **This is why (a1) is the safe spike.**
- **(a2) general `bytes.split`/`bytes.decode` faithful model:** **NOT corpus-inert** —
  every module with bytes/string flow re-emits. Expect a non-trivial subset of the 12
  `.split`/`.decode` modules (and possibly more via `_coerce_to_int` string-arg
  changes) to byte-diff. This is a deliberate **re-bless**, not a regression — but it
  must be handled as corpus churn: run `bin/byte-diff-sweep.sh` against a baseline,
  audit each diff is the intended faithful-string change (no semantic regression), and
  re-bless the baseline.

### 5.3 Must-not-regress

- The **landed write-side dirscan retirements** (`_write_dir_entry`/`_zero_entry`/
  `_write_entry` + `_blit_*`) must stay 0 non-Valid. Milestone-0 §4 confirmed the new
  read marker does not poison them; (a1) touches only the read body, so the risk is low
  — but the spike must re-run the per-helper scan (§6) to confirm no relocated explosion.
- The os `__init__` gate (1182/0) and the full body gate baseline must not red.
- The global change (a2) must not flip any currently-green corpus module to a worse
  emission that fails L3-typecheck (the `unbound type symbol 'array'` class of emitter
  fragility, `pycsl-monitoring` A.8) — audit the byte-diff for type-correctness.

---

## 6. DE-RISKING SPIKE + ROLLOUT

### 6.1 The smallest experiment (os-name-only, option (a1))

**Goal:** make JUST the dir-entry name read faithful and measure whether
`_dir_lookup`'s `slot_name == pathname` branch discharges in the FULL gate ×2,
composing with the banked value marker.

1. On a throwaway worktree at clean HEAD, **apply `getting-better/SPIKE-dir-lookup-value.patch`**
   (the banked, cross-validated value marker + `0720.proofs`).
2. **Make the read name faithful (a1):** lower the `_dir_lookup` body's `name` to
   `field_to_str(self.dir, entry_offset+2, 30)` (special-case the
   `split(b'\x00')[0].decode(...)` idiom, OR — for the spike — hand-edit the emitted
   `.mlw` / add a minimal emitter recognizer). Cite `slot_name_byte_decode` (already a
   `#@ proof` available).
3. **Re-run the FULL gate ×2** (`PYTHONHASHSEED=0 pycsl pure_lib/os/UnixInodeFileSystem.py
   --no-typecheck`, Alt-Ergo + Z3, 30s/goal). Decision criterion:
   - **YES** (the 4 `_dir_lookup` non-Valid goals from Milestone-0 §3 go Valid, both
     runs, write side still 0): Gap-5 is sufficient → proceed to rollout (a2) +
     retire the read-side dirscan trio.
   - **NO** (the marker step now fires but the goal still explodes A.7-style): Gap-5 is
     *necessary but not sufficient* — the wall is module-scope/aggregate-context
     (`pycsl-monitoring` row "A.7 ... apparatus-context feasibility"), not the codec.
     Then the read side is blocked on the SAME scope/module-emission problem as the
     write side, and the L–XL string rollout should be **deferred** until scope-emission
     lands.
4. **Per-helper scan** (Milestone-0 §4 shape): confirm write-side helpers stay 0
   non-Valid (no relocated explosion).
5. **Soundness probe** (`pycsl-monitoring` B catalog): on any newly-Valid read ensures,
   add a `#@ requires` forcing a non-canonical disk (e.g.
   `slot_inode(self.dir,5,0)==3`); the read consequence must still hold (it is a faithful
   decode, so it should) — confirm it is not an empty-disk artifact.

### 6.2 Broader rollout (only if 6.1 = YES)

Promote (a1) → (a2): faithfully model `bytes.split`/`bytes.decode` over `array int`
generally (the no-more-int endpoint). Then: byte-diff sweep against baseline → audit →
re-bless; retire `_dir_lookup`/`_dir_find_slot`/`_dir_find_free` `\trusted` (read-side
trio 4→1, only `sys_rename`'s residual remaining), and re-attempt fd-resolution
(`sys_open` `fd-resolution-fidelity`, which `pycsl-monitoring` A.14 flagged as blocked
on "the dir_lookup correspondence folded into a cross-validated predicate" — Gap-5
faithful names are a prerequisite there too).

---

## 7. HONEST COST/BENEFIT + RECOMMENDATION

- **Effort:** spike S–M (small code; the cost is the full-gate measurement). General
  rollout L–XL (a global string-lowering change with managed corpus churn).
- **Biggest risk:** (1) the faithful name **still doesn't bridge** in the full gate —
  Milestone-0 already showed the value-marker half hits an A.7 aggregate-context
  explosion one layer up; Gap-5 removes the *type/dependence* obstruction but may
  expose the *module-scope* obstruction underneath. (2) The general fix is a large
  string-lowering change with non-trivial corpus re-bless (12 `.split`/`.decode`
  modules, broader via string-literal coercion).
- **Cheaper scopes:** os-name-only (a1) is the cheap, near-inert spike; do NOT pay the
  general (a2) cost until (a1) proves Gap-5 is sufficient.
- **Payoff (if it lands):** unblocks the read-side dirscan trio (`\trusted` 4→1),
  likely fd-resolution, AND advances the no-more-int doctrine broadly (retires a
  pervasive str→int leak). The bridge is already cross-validated, so the soundness
  upside is unusually clean — this is one of the rare gaps where the *correct* fix also
  *shrinks* the TCB.

**Calibrated call: BUILD THE SPIKE (a1) now.** It is cheap, it is the doctrine-faithful
direction, and it resolves the single open empirical question — is Gap-5 *sufficient*
or merely *necessary* — that the L–XL decision hinges on. **Defer the general (a2)
rollout** until the spike's full-gate ×2 verdict is YES; if it is NO, the priority is
the module-scope/aggregate-context emission problem, not the name codec.

---

## 8. APPENDIX — evidence index (file:line)

- Read-side NO: `getting-better/20260619-2230-dir-lookup-milestone0-NO.md` (§3 the 4
  non-Valid, §5 the syntactic wall, §6 "model the byte→str RECOVER (Gap-5)").
- The hash: `src/pycsl/module6_whyml/identifiers.py:8-16` (`stable_hash`).
- The leak sites: `expressions.py:402-412` (`_str_operand_to_int`), `:1276-1285`
  (`decode`), `:1284`+`:163` (`_coerce_to_int` hashes decode arg), `:1308-1317`
  (generic path coerces `split`'s array receiver to `Array.make 1 0`), `statements.py:101-111`
  (`_decode_to_string` scoping).
- The read bodies: `pure_lib/os/UnixInodeFileSystem.py:983, 1035` (the
  `split(b'\x00')[0].decode(...)` idiom), `:973/1025/1054` (the 3 trusted read helpers),
  `:957-959` ("Gap 5, unmodeled").
- The faithful encode symbols: `preamble.py:1132` (`field_to_str` logic function),
  `:942-950` (`field_to_str_round_trip`), `:986-991` (`field_to_str_frame`), `:324`
  (`slot_name_byte_decode` bridge). Proofs: `0708`/`0712`/`0714`/`0720.proofs/`.
- Reproduced lowering (this run, `/tmp`, cleaned): read body → `name := decode_1
  1501791143; !name = str_hash_op pathname`; str-typed target → `decode_str_1
  1501791143` (string, still hash-arg); `split` → `nb_split_1 (Array.make 1 0) : int`
  (disk bytes discarded at split).
- Blast radius: 38 `.expected.mlw` fixtures (0 reference the symbols); 670 corpus
  `0*.py` swept by `bin/byte-diff-sweep.sh`; 12 `.split`/`.decode` modules; 661
  string-literal modules.
