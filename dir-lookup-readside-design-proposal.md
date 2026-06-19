# Design Proposal — retiring the READ-side dirscan trio (`_dir_lookup` / `_dir_find_slot` / `_dir_find_free`)

**Status:** DESIGN ONLY — no `src/` or `pure_lib/` change. Read-only analysis grounded in file:line.
**Scope:** os `\trusted` 4 → 1 (retire the 3 `dirscan-fidelity` READ helpers; leave only `fd-resolution-fidelity`).
**Author:** test-supervise-sl design pass, 2026-06-19.
**Reviewed inputs:** `getting-better/20260619-2008-dir-lookup-4to3-GAP.md` (the just-merged read-side GAP, PR #44), `test-supervise-sl.md` (extreme-rigor doctrine), `config/skills/pycsl-monitoring/SKILL.md` (Gate-S knowledge base).

---

## 0. RECOMMENDATION (read this first)

**SPIKE-FIRST. Effort: L (large), with a real chance of escalating to XL.**

The read-side trio is **not** an unbounded structural wall like the GAP doc concluded in isolation
— the write-side retirements (#41/#42/#43, landed) supply a **directly transferable blueprint** (the
`dir_blit_marker` family: a unique marker atom carrying a *value* conclusion across SMT, cross-validated
zero-TCB). The two missing pieces the GAP doc names are both, in principle, the **read-side duals of
machinery that now exists**:

1. a `dir_lookup`-**VALUE** axiom (dual of the *sign-IFF* `scan_reflects_present`), and
2. a byte→str **RECOVER** name codec (dual of the str→byte ENCODE round-trip `field_to_str_round_trip`).

So this is **not** a "keep-as-GAP forever" verdict. But it is **also not** a green-light build: the
single biggest risk (§8) is that the value axiom's trigger re-introduces the *gap-9 existential
explosion* that `scan_reflects_present` was deliberately shaped (sign-only) to avoid, AND that the read
helper's body — unlike the write helper's controllable literal blit — reads through `Array.sub` +
opaque `_unpack_direntry` + an opaque `decode_1` name constant, giving **no lever** to surface the
marker's byte antecedents. The honest move is a **bounded Milestone-0 spike** (§7) whose single
go/no-go question is: *does a marker-keyed `dir_lookup`-value axiom let `_dir_lookup`'s fidelity
ensures discharge in the FULL body gate (not `--fun`)?* If the spike greens, build the trio (it is
mechanical generalization). If it reds with the same A.7 aggregate-context explosion the write side
hit at `_write_dir_entry` (catalog-B rows, SKILL.md §B), **keep all three as logged GAPs** — the
read-side then has no cheaper lever than the write side did, and the write side took five PR-cycles +
a marker architecture to land just *three* helpers.

A cheaper, higher-confidence alternative target exists (§8): the **`fd-resolution-fidelity`** trust on
`sys_open` — but note SKILL.md A.14 already records that this is a *distinct, also-hard* wall (it
needs the same dir_lookup correspondence folded into a predicate). It is **not** obviously easier;
it may in fact *depend on* the read-side work proposed here.

---

## 1. Problem statement (the wall, with evidence)

### 1.1 Target & current trust inventory (verified)

The os-gated module is `pure_lib/os/UnixInodeFileSystem.py`. It carries **exactly 4** `#@ \trusted`
directives (verified by grep + per-line `def` resolution):

| Line | Helper | Trust class | Side |
|---|---|---|---|
| `UnixInodeFileSystem.py:972` | `_dir_lookup` | `dirscan-fidelity` | READ |
| `UnixInodeFileSystem.py:1024` | `_dir_find_slot` | `dirscan-fidelity` | READ |
| `UnixInodeFileSystem.py:1054` | `_dir_find_free` | `dirscan-fidelity` | READ |
| `UnixInodeFileSystem.py:1556` | `sys_open` | `fd-resolution-fidelity` | (fd) |

The 3 WRITE-side dirscan trusts are **retired and intact**: `_write_dir_entry` (#41, 7→6),
`_zero_entry` (#42, 6→5), `_write_entry` (#43, 5→4), via the `dir_blit_marker` family. Confirmed in
`git log` (commits `4308cd6` / `6db50b9` / `03006a1`) and by the marker cites now living on those
helpers (`UnixInodeFileSystem.py:1130-1135`, `:1177` asserts the marker atom). The just-merged
`a00e2b6` banked the read-side as a GAP. **"4→1" = retire the read-side trio.**

### 1.2 `_dir_lookup`'s fidelity ensures (the load-bearing claim)

`_dir_lookup` (`UnixInodeFileSystem.py:973-986`) carries two postconditions; the body is a 16-slot
scan that reads `entry = self.dir[entry_offset:entry_offset+32]`, calls `_unpack_direntry`, decodes
the name, and keeps the last live match (`found = inode_num`). Its trusted claim is a **VALUE
equality** (paraphrased from the body + GAP doc §1):

```
ensures \result == dir_lookup(self.dir, block_num, pathname)     # FIDELITY (load-bearing)
ensures \result == -1 or (\result >= 1 and \result < 32)          # RANGE
```

`_dir_find_slot` (`:1024`) trusts `slot_inode(self.dir,5,\result) != 0` **and**
`slot_name(self.dir,5,\result) == pathname` — i.e. the recovered name of the returned slot equals the
query (a byte→str RECOVER claim). `_dir_find_free` (`:1054`) trusts
`slot_inode(self.dir,5,\result) == 0`. All three are read-side decode-vs-bytes value/recover claims;
they share one wall.

### 1.3 The `dir_lookup` registry is RELATIONAL ONLY — no value form

Enumerating **every** `dir_lookup`-touching axiom in `src/pycsl/module6_whyml/preamble.py`:

- `scan_reflects_present` (`:123-131`) — **sign-IFF only**: `dir_lookup disk blk name >= 0 <-> (∃k live match)`.
- `dir_lookup_present_witness` (`:171-176`) — present-witness: a live match ⟹ `dir_lookup ... >= 0`.
- `dir_lookup_present_zero_frame` (`:195-204`) — cross-state presence carry across a zero.
- `dir_lookup_frame` (`:762-768`) — **frame**: disks agreeing on every slot decode have **equal**
  `dir_lookup` (`= dir_lookup` *between two disk states*, NOT a value in terms of `slot_inode`).
- `remove_reflects_absent` (`:343-351`) / `remove_unique_absent` (`:378-388`) /
  `dir_lookup_remove_absent` (`:409-419`) — give `dir_lookup ... < 0` under absence hypotheses.

**None states `dir_lookup`'s VALUE** (e.g. `dir_lookup disk blk name = slot_inode disk blk <the last
live matching slot>`). The three backing symbols are uninterpreted `val function`s
(`preamble.py:1212-1214`):

```
val function slot_inode (disk: array int) (blk: int) (k: int) : int
val function slot_name  (disk: array int) (blk: int) (k: int) : string
val function dir_lookup (disk: array int) (blk: int) (name: string) : int
```

So even with the range postcondition proven from the loop invariant, the **fidelity ensures has no
axiom to land on** — it is a value equality against an uninterpreted symbol constrained only by
sign/frame/absence facts. This is the keystone obstruction (GAP doc §3c).

### 1.4 The de-trust spike result (cited, not re-derived)

GAP doc §2: removing the `\trusted` and running `--fun unixinodefilesystem___dir_lookup` →
**both postconditions FAIL** (`Out of memory` 11–13s; `Timeout` 192774 steps). Isolation probes show
even the *trivial range* ensures OOMs/Timeouts because the module preamble emits **22 axioms** (the
full `UnixFs.Dir.*` web) in scope even under `--fun` — catalog-B "A.7 aggregate-context pollution"
(SKILL.md §B). A de-trust that reds the gate is a REGRESSION (doctrine HARD CONSTRAINT), so the
directives stayed. This proposal addresses *both* the missing logic (the value axiom) **and** the
aggregate-context explosion (the trigger discipline + the de-risking spike's full-gate measurement).

---

## 2. Current modeling analysis

### 2.1 How `dir_lookup` is axiomatized today — and WHY the value form was avoided

The Rocq kernel `unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixDirScan.v` **does** compute the
value. The scan is a `Fixpoint` over the slot prefix (`UnixDirScan.v:50-62`) that keeps the *last*
live matching slot's `slot_inode`, and `dir_lookup` is **defined** as `scan d blk name 16 (-1)`
(`UnixDirScan.v:131`). The kernel proves only `scan_reflects_present` — the **sign-IFF**
(`UnixDirScan.v:134-138`), via `scan_reflects_prefix` (`:67-70`), an induction over the prefix length.
**There is no value lemma** (`grep Lemma/Theorem UnixDirScan.v` returns only sign/witness/frame
theorems).

WHY the value form was deliberately omitted (the "gap-9 existential explosion"): the registry comment
at `preamble.py:109-122` records that `scan_reflects_present` is "INDUCTIVE over the slot loop (SMT
times out: **gap-9, 14.6M/11.6M/18.8M steps**)" and is therefore offloaded to the kernel and exposed
*only as the IFF*. The `dir_lookup_present_witness` comment (`preamble.py:150-161`) is explicit about
the trigger hazard: `scan_reflects_present`'s IFF "triggers on every `dir_lookup` term, so in
sys_rename's final state it introduces the matches-∃ for BOTH the present name AND the absent name …
the E-matching balloon." A **value** axiom of the shape `dir_lookup = slot_inode disk blk <witness k>`
re-introduces *exactly* that existential witness `k` into the goal — the very thing the sign-only
exposure was crafted to suppress. **This is the design constraint the value axiom must defeat (§3.1).**

### 2.2 The name codec — ENCODE direction exists, RECOVER direction is the Gap-5 wall

The string↔byte field codec is `field_to_str` (`preamble.py:1132`, an uninterpreted `function`).
Two ENCODE-direction facts are registered and cross-validated:

- `field_to_str_round_trip` (`preamble.py:942-950`, exhibit `0708.proofs/`): the **ENCODE→DECODE**
  direction — given a `name` is byte-for-byte present (`d[off+i] = ord(name[i])`), null-terminated,
  fits the field, no embedded null ⟹ `field_to_str d off width = name`. Proved by string
  extensionality in the kernel (SMT cannot — the ~23M-step string E-match wall, `preamble.py:929-933`).
- `field_to_str_frame` (`preamble.py:986-991`, exhibit `0714.proofs/`): byte-window agreement ⟹ equal
  decode.
- `slot_name_byte_decode` (`preamble.py:321-324`, exhibit `0712.proofs/`): the bridge
  `slot_name disk blk k = field_to_str disk (blk*512+32*k+2) 30`.

The **RECOVER** direction (GAP doc §3b, "Gap 5") is the dual: *given the disk bytes at a slot, what
name does the query compare against?* The read body's emitted `name` lowers to an **opaque hash
constant** (`name := decode_1 1501791143`, GAP doc §3b) with **zero dependence on `self.dir` bytes** —
because the byte→str RECOVER codec is unmodeled. The compare `name == pathname` lowers to
`str_hash_op pathname`, and there is **no bridge** from this opaque constant to
`slot_name(self.dir, 5, i)`. The write side never hit this: it *writes* the bytes it controls (so
`name → bytes` ENCODE suffices). The read side must *recover* the name from bytes through the opaque
codec — the unmodeled direction.

**Important nuance:** `_dir_lookup`'s fidelity ensures (`\result == dir_lookup(...)`) does **not**
directly need a name in terms of `slot_name` — the `dir_lookup` symbol already abstracts the whole
name-matching scan. The Gap-5 RECOVER wall bites hardest on `_dir_find_slot`'s
`slot_name(self.dir,5,\result) == pathname` ensures (it *names* a slot's recovered name), and on
*connecting the body's per-slot compare to the abstract scan* (see §3.2). So the two pieces have
different exposure: `_dir_lookup` is primarily the value-axiom problem; `_dir_find_slot` is
value + RECOVER.

### 2.3 The banked scan kernels — what they prove and why they're relational-only

`unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan{,Absent}.{v,lean}`,
`DirLookupFrame`, plus `scan_reflects_present` / `LookupFrame` prove the scan **structure** over an
**abstract** decode (`Variable slot_inode` / `Variable slot_name`, `UnixDirScan.v:31-34`) and the
sign-IFF + frame. They are exactly the **relational** facts the *callers* of `_dir_lookup` consume
(presence/absence through the public os wrappers — `sys_open` ENOENT, `sys_unlink`, `sys_rename`). They
deliberately abstract the byte↔decode bridge away (that is the Gap-5 codec) and expose **no VALUE form
of `dir_lookup`** — even though the underlying `scan` Fixpoint computes one. They are relational-only
*by construction*, to keep the abstract model E-matching-safe for the callers (§2.1).

---

## 3. The two needed pieces, designed

### 3.1 Piece A — a `dir_lookup`-VALUE axiom with a NON-EXPLODING trigger

**Goal statement (closed-form value).** From the kernel `scan` semantics (`UnixDirScan.v:50-62`),
`dir_lookup disk blk name` equals the `slot_inode` of the *last live in-range matching slot* (or `-1`
if none). The naive value axiom

```
forall disk blk name k. (0<=k<16 /\ slot_inode disk blk k <> 0 /\ slot_inode disk blk k < 32
                          /\ slot_name disk blk k = name /\ <k is the last such>)
                         -> dir_lookup disk blk name = slot_inode disk blk k
```

is correct (provable in-kernel as a new theorem over `scan`) but its trigger would have to fire on
`dir_lookup` + a witness `k`, re-introducing the existential matches-∃ that gap-9 forbids (§2.1).

**The non-exploding design — mirror the write-side `dir_blit_marker_value_inode` discipline.** The
write side faced the *identical* dilemma (a value conclusion `slot_inode d1 5 s = 256*b0+b1` that, if
keyed on the abstract `slot_inode` atom, poisons every byte mutator) and solved it with a **unique
marker atom** (`preamble.py:506-555`, `dir_blit_marker_intro` + `dir_blit_marker_value_inode` at
`:668-672`). The marker fires **exactly once**, at the genuine apply site
(`#@ assert dir_blit_marker(...)`, `UnixInodeFileSystem.py:1177`), never on a bare `disk[...]` read.

The read-side dual: introduce a **unique read-side scan marker** — call it
`dir_scan_result d blk name r` — declared in `_AXIOM_FUNCTIONS["UnixFs.Dir."]`, keyed on
`[dir_scan_result d blk name r]` (unique, like `dir_blit_marker`), with two cross-validated facts:

- **`dir_scan_result_intro` (DEFINITIONAL, zero trust).** The marker is conservatively DEFINED by the
  *body's own loop result*: from the loop invariant (`found` is `-1` or the inode of a live matching
  slot scanned so far), establish the marker atom at loop exit. This is the read-side dual of
  `dir_blit_marker_intro` building the marker from the blit's byte facts. The intro fires only on the
  marker atom, so it never matches a bare scan term.
- **`dir_scan_result_value` (cross-validated).** `dir_scan_result d blk name r -> dir_lookup d blk name = r`.
  This is the *new* value lemma, proved in the kernel over the `scan` Fixpoint (the
  last-live-match argument), keyed on the marker — fires **exactly once** at the asserted atom, so the
  existential witness `k` is **discharged offline in the kernel** and never enters the WhyML goal.

**Why this composes with the relational axioms without contradiction.** `dir_scan_result_value`
concludes `dir_lookup = r` where `r` is the body's actual `found`. The sign-IFF
`scan_reflects_present` then *follows* (`r >= 0` iff a live match exists is already the IFF) — they
agree on the sign, and the value axiom only *refines* it. There is no double-modeling contradiction:
the value axiom is a **strict consequence** of the same `scan` definition `scan_reflects_present` is a
consequence of (both are theorems over `UnixDirScan.v:50-62`), proved together in one kernel section.
Soundness is the kernel's (Rocq Closed-under-global-context + Lean ⊆ {propext, Quot.sound}), exactly
the `dir_blit_marker` bar. **This is the read-side `dir_blit_marker_value_inode`.**

### 3.2 Piece B — the read-direction name codec (Gap-5 RECOVER)

The body's per-slot compare is `name == pathname` where `name` is the opaque `decode_1` constant
(§2.2). To bind the body's scan to the abstract `dir_lookup`, the marker intro (3.1) must establish,
per scanned slot, that *the body's `name` for slot `k` equals `slot_name disk blk k`* — i.e. the
byte→str RECOVER bridge.

**Assess: does `field_to_str_round_trip` already suffice?** **No, not directly.** The round-trip is
ENCODE→DECODE (`bytes-present-for-name ⟹ field_to_str = name`); it requires the *name as a hypothesis*
(you must already have the name to assert its bytes are present). The read side has the **bytes** and
wants the **name** — that is the RECOVER direction. Two sub-options:

- **B1 (fold the recover INTO the marker — preferred).** Do not model a standalone byte→str recover
  function at all. Instead, have `dir_scan_result_intro` take the body's `name` and the slot bytes as
  hypotheses and discharge `slot_name disk blk k = <body name>` *inside the kernel proof* (where
  `slot_name` is the concrete `field_to_str (off+2) 30` of `0712`/`0708`'s model, and the scan-to-
  first-null decode is a kernel `Fixpoint`). This is **exactly** how the write side handled the name:
  `dir_blit_marker_at_value_name` (`preamble.py:730-734`) concludes `slot_name d1 blk s = name` with
  the round-trip "discharged INSIDE the 0718 kernel proof, so the os body provides ONLY the marker atom
  and never materializes the string codec (field_to_str) in its VC" (`preamble.py:727-728`). The read
  side does the dual: the recover reasoning lives in the kernel behind the marker; the os body never
  materializes `field_to_str`. **This avoids modeling a new recover function — it reuses the existing
  `field_to_str` model in a new kernel direction.** BUT it requires the body to *surface the slot
  bytes* to the marker intro (§3.3 — the lever problem).
- **B2 (a standalone `str_to_field` / recover lemma).** Model the recover as its own cross-validated
  axiom `field_to_str d off width = s -> (the s is the unique scan-to-first-null name)`. Heavier (a new
  symbol + new exhibit `0720`-style), and it still needs the body to surface the bytes. **Not
  recommended** unless B1's marker proof proves intractable — it adds a symbol to the TCB surface for
  no benefit over folding into the marker.

**Recommendation: B1.** The recover direction is **dischargeable in the kernel today** (the `0708`/
`0712` model already has the scan-to-first-null `field_to_str` and proves extensionality both ways is
feasible; the round-trip proof at `0708.proofs/.../FieldToStrRoundTrip.{v,lean}` is a string-
extensionality argument that generalizes). The blocker is **not** the kernel proof — it is the body
lever (§3.3).

### 3.3 The lever problem (the read-side-specific obstruction the write side did not have)

The write helper *controls* its byte writes, so it could be restructured to a **literal-offset blit**
(`5*512 + 32*slot`, no `!entry_offset` ref) that makes the marker's byte antecedents
(`d1[2560+32*s] = b0`) syntactically present (SKILL.md §A "literal-offset blit `5*512 + 32*slot`").
The read helper reads through `entry = self.dir[entry_offset:entry_offset+32]` (an `Array.sub`) +
`_unpack_direntry` (opaque) — it produces **no `self.dir[blk*512+32*k]` term** (GAP doc §3a), so the
marker intro's byte antecedents never E-match the body.

**The fix is the SAME restructuring lever, applied to the read body:** rewrite `_dir_lookup`'s loop to
read the slot fields by **literal byte offsets** (`self.dir[5*512 + 32*i]`,
`self.dir[5*512 + 32*i + 1]`, and the name-field bytes) instead of `Array.sub` + `_unpack_direntry`.
This is a faithful refactor of the same scan (it reads identical bytes) that surfaces the byte terms
the marker intro keys on. It is the read-side dual of the write-side "literal-offset blit." **This is
the single highest-risk engineering step** (§8): the write side needed an opaque-offset *byte-only
sibling helper* (`#@ sibling_concrete`, `UnixInodeFileSystem.py:1091` `_blit_dir_entry`) to keep the
byte loop from re-exploding the invariant web, and the read body may need the analogous
`#@ sibling_concrete` byte-only slot reader so its per-iteration byte terms don't drag the marker
conclusion into every loop-invariant VC.

---

## 4. Soundness — the bar (non-negotiable)

Both new pieces must clear the **identical bar the `dir_blit_marker` family cleared** (the doctrine,
`test-supervise-sl.md` §Doctrine; SKILL.md "BINDING"):

1. **`dir_scan_result_intro` is DEFINITIONAL → zero TCB.** Like `dir_blit_marker_intro`
   (`preamble.py:535`, "DEFINITIONAL, zero trust") and `block_content_eq_intro`
   (`preamble.py:217`), the marker is *conservatively defined* by its hypotheses (one direction of
   `marker <-> body-result`). Definitional intro/elim add **no** axiom to the TCB. This is doctrine
   option (b) (restructured/folded proof), not even an axiom.
2. **`dir_scan_result_value` is a CROSS-VALIDATED axiom → human-gated TCB, but bounded.** It is a new
   *theorem* over the existing `scan` Fixpoint, proved in BOTH Rocq (Closed under the global context /
   Section-Variables-only) and Lean (`#print axioms ⊆ {propext, Quot.sound}`), cited via
   `#@ proof rocq|lean`. This is the **same trust class** as `scan_reflects_present` itself
   (`preamble.py:115-116`) and every marker value fact (`dir_blit_marker_value_inode`,
   `preamble.py:665-667`). It is *PROVING in a kernel*, not a bare `\trusted` — but adopting it is a
   **human-gated TCB decision** (the doctrine permits it only via human sign-off; the loop may not
   take it autonomously).
3. **Consistency with the relational axioms (no double-modeling contradiction).** Both
   `scan_reflects_present` (sign) and `dir_scan_result_value` (value) are theorems over the *same*
   `scan` definition (`UnixDirScan.v:131`). Proving them in **one kernel section** over one `scan`
   guarantees they cannot contradict (a model with a satisfying `scan` satisfies both). The proposal
   **must** add the value theorem to `UnixDirScan.v` (not a fresh, independently-axiomatized symbol) —
   this is the soundness chokepoint. A value axiom over a *new* abstract `dir_lookup'` symbol would be
   double-modeling and is **disqualified**.
4. **Re-verification gate.** The cited axioms must survive `--reverify` (a cited axiom that secretly
   re-assumes a property surfaces as a kernel `Axiom`/extra Lean axiom and fails, SKILL.md A.10). The
   exhibit (`0720.py`-style) must verify SUCCESS and the proofs persisted under
   `test-suite/corpus/pycsl-reference/0720.proofs/{rocq,lean}/`.

**Disqualifier check (passes):** no piece relocates trust into an assumed-not-proven value axiom — the
value fact is kernel-proven over the same Fixpoint as the existing sign fact. The recover (B1) is
folded into the cross-validated marker intro, no new trusted symbol.

---

## 5. Design options + trade-offs (≥2)

### Option (a) — Full `dir_lookup`-VALUE marker axiom + folded recover (B1) [RECOMMENDED if spike greens]

The design of §3: `dir_scan_result` marker (intro definitional + value cross-validated), recover folded
into the intro's kernel proof, literal-offset body restructure + `#@ sibling_concrete` byte reader.

- **Soundness:** Strongest. Value fact kernel-proven over the *same* `scan` as the sign fact (§4.3);
  recover folded into a definitional/cross-validated marker; zero new abstract symbols beyond the
  marker (which is conservatively defined). Clears the `dir_blit_marker` bar.
- **Blast radius:** The marker is emission-gated + UNCITED ⇒ corpus byte-diff **0** (the
  `dir_blit_marker` family is already corpus-inert, SKILL.md §B; the new marker follows the same
  registry pattern, `preamble.py:689` "trigger … is UNIQUE, so it fires ONLY at … the asserted marker
  atom, NEVER inside a sibling byte mutator"). The body restructure of `_dir_lookup` is local; it must
  not change the **range** postcondition or the public wrappers' consumed relational facts (it does
  not — the value axiom *refines*, the sign-IFF still holds).
- **Effort:** L. One marker family (4 axioms, mirroring `dir_blit_marker`), one kernel theorem added
  to `UnixDirScan.v` (+ Lean mirror), one exhibit, three body restructures (the trio shares the
  pattern — `_dir_find_slot`/`_dir_find_free` are the same scan with a different `found` rule, so they
  reuse the marker with a slot/inode value vs an inode value).
- **Closes the value equality?** YES — directly: `dir_scan_result_value` gives
  `dir_lookup = found = \result`.
- **Risk:** the A.7 aggregate-context explosion at the genuine apply site (the *write side* hit this at
  `_write_dir_entry` even with the marker — SKILL.md §B "marker fires EXACTLY ONCE … BUT the FULL body
  gate STILL reds … the os axiom web starves its step budget"). The read trio lives in the SAME module
  with the SAME 22-axiom web. **This is what the spike (§7) must settle.**

### Option (b) — per-helper scan-loop-invariant, NO global value axiom

Strengthen `_dir_lookup`'s loop invariant to carry `found == dir_lookup(self.dir, blk, name)`
incrementally (the loop-prefix invariant the kernel's `scan_reflects_prefix` proves), discharging the
fidelity ensures inductively in WhyML directly, using only the existing kernels.

- **Soundness:** Best (zero new axiom — pure restructured proof, doctrine option (b)).
- **Closes the value equality?** **NO — this is exactly the gap-9 explosion.** The loop-prefix value
  invariant is `scan_reflects_prefix` (`UnixDirScan.v:67`), which the registry comment records SMT
  **times out** on (14.6M/11.6M/18.8M steps, `preamble.py:111-112`) — that is the *whole reason* it
  was offloaded to the kernel and exposed only as the sign-IFF. The existing kernels prove the
  *structure* over an abstract decode but provide **no WhyML value rung** for the loop to cite per
  iteration. So the loop invariant cannot be discharged by SMT, and there is no per-iteration value
  axiom to cite. **Rejected** — it re-opens the wall the abstract model was shaped to close.

### Option (c) — restructure the read helpers to return via a marker-style folded atom (no value at all)

Have `_dir_lookup` return an opaque folded `dir_scan_result` atom and *defer* the value equality to the
caller (the syscalls) where the relational facts suffice.

- **Soundness:** Fine (folded atom, definitional).
- **Closes the value equality?** **NO** — it dodges the fidelity ensures rather than discharging it.
  The `\trusted` is **all-or-nothing per method** (SKILL.md §B "A trust is all-or-nothing per
  method"); leaving the value ensures unproven (even if callers don't need it) means the trust **stays**.
  Also the callers *do* consume the value in places (e.g. `sys_open` returning the looked-up inode).
  **Rejected** as a retirement (it is a re-modeling, not a discharge).

**Verdict:** Only Option (a) actually retires the trust soundly. Options (b)/(c) are recorded to show
they were considered and why they fail — (b) is the gap-9 trap, (c) is not a retirement.

---

## 6. Blast radius / corpus inertness

- **Emission-gated, opt-in, byte-diff 0.** The new marker + value axiom enter `_AXIOM_REGISTRY` /
  `_AXIOM_FUNCTIONS` UNCITED-by-default (the established pattern: every `dir_blit_marker` axiom is
  present-but-uncited for non-os modules, corpus byte-diff **0/shared**, SKILL.md §B repeatedly; the
  registry is keyed so an axiom is emitted only when a `#@ proof` cites it or a contract references its
  symbol, `preamble.py:1186-1188`). Only `pure_lib/os/UnixInodeFileSystem.py` would cite them ⇒
  corpus byte-diff **0** for all non-citing modules (must be measured: `bin/byte-diff-sweep.sh`).
- **Doc-coherency.** No new `#@` directive is added (the marker is a registry axiom + a body
  `#@ assert`/`#@ proof` citation, both existing surfaces) — so `bin/doc-coherency.py --check` is
  unaffected. IF the body restructure needs a new `#@ sibling_concrete`-class directive (it should not
  — that directive exists), the doc-coherency invariant (`config/skills/pycsl-doc-coherency`) would
  apply.
- **Must NOT regress the 3 landed write-side retirements.** They cite the `dir_blit_marker` /
  `field_to_str` family (`UnixInodeFileSystem.py:1130-1135`). The new read-side marker uses a
  **distinct unique atom** (`dir_scan_result`, never `dir_blit_marker`), so it cannot fire inside the
  write helpers' VCs. **Regression test:** re-run the os body gate + `__init__` gate + the full
  `formal_os_*` suite after the change; the write-side helpers must remain Valid with their existing
  cites. (SKILL.md A.14 / os-gate-blind-spot: green `__init__` is NOT sufficient — run the public
  formal tests too.)

---

## 7. De-risking spike + incremental rollout

### Milestone-0 spike (the SINGLE go/no-go) — hand-built `.mlw`, ~1–2 days

Mirror the write-side Milestone-0 pattern (the `dir_blit_marker` spikes were de-risked in `/tmp`
hand-built `.mlw` before landing). **The spike's only question:** *does a marker-keyed
`dir_lookup`-value axiom let `_dir_lookup`'s fidelity ensures discharge in the FULL body gate
(PYTHONHASHSEED=0, Alt-Ergo + Z3, NOT `--fun`, run ×2 for non-determinism)?*

1. Add `dir_scan_result` to `_AXIOM_FUNCTIONS["UnixFs.Dir."]`; add `dir_scan_result_intro`
   (definitional) + `dir_scan_result_value` (stated; kernel proof **stubbed/admitted for the spike
   only** — the spike tests SMT *applicability*, not soundness, which is settled separately in the
   kernel).
2. Restructure a **copy** of `_dir_lookup`'s body to literal byte offsets (`5*512+32*i`) + a
   `#@ sibling_concrete` byte-only slot reader; assert `dir_scan_result(self.dir, 5, pathname, found)`
   at loop exit; cite `dir_scan_result_value`.
3. Run the **FULL** os body gate (not `--fun`). 
   - **GREEN (fidelity + range Valid, no new residual, write-side helpers still Valid):** the marker
     defuses the aggregate-context explosion at the read site → **proceed to build.** Then complete the
     kernel proof (un-stub the admit; cross-validate Rocq + Lean), the exhibit, and `--reverify`.
   - **RED (OOM/Timeout in the full module, as the write side hit at `_write_dir_entry`):** this is the
     A.7 wall the write side needed a *module-split or trigger-tuning* follow-on for (SKILL.md §B,
     `20260619-0905-write-dir-entry-7to6-modulesplit-GAP.md`). **Stop. Keep as logged GAP.** The
     read-side then has no cheaper lever than the (still-open) write-side scope/module-emission feature.

**Soundness probe (mandatory in the spike, per catalog-B "empty-disk artifact" + "vacuity" rows):**
add `#@ requires slot_inode(self.dir,5,0)==3` (a non-canonical disk) and a falsification
(`#@ assert <branch-guard> ==> 1==0`). If the ensures still proves under the non-canonical disk AND the
falsification is NOT Valid, the green is real (not an empty-disk/in-place-collapse artifact).

### Generalization to the trio (only if M0 greens)

`_dir_find_slot` returns the *slot index* of a live match (value = slot, recover = name); `_dir_find_free`
returns a *free slot* (value = slot with `slot_inode == 0`). Both are the same scan with a different
`found` rule. Reuse the `dir_scan_result` marker with two sibling value facts
(`dir_scan_result_slot_live` / `dir_scan_result_slot_free`), each a corollary of the same kernel
section — exactly as the write side exposed `value_inode` / `value_name` / `frame_only` as separate
marker-keyed corollaries of one `dir_blit_marker_insert` proof (`preamble.py:624-672`). Mechanical once
M0 proves the pattern works in-module.

---

## 8. Honest cost/benefit + recommendation

**Effort:** **L** for Option (a) if M0 greens; escalates to **XL** if M0 reds and the only close is the
unbuilt module-scope-emission feature (the write side's still-open follow-on,
`20260619-0905-...-modulesplit-GAP.md`).

**Benefit:** os `\trusted` 4 → 1 — a real, principled TCB reduction (3 of the remaining 4 trusts gone),
completing the dirscan retirement that the write side started. High value: it would mean the entire
directory-scan layer (read + write) is kernel-grounded, leaving only `fd-resolution-fidelity`.

**The single biggest risk:** the **A.7 aggregate-context explosion at the genuine apply site.** The
write side proved (SKILL.md §B, catalog row "The A.7 too-many-axioms-in-scope diagnosis is REFUTED")
that the explosion at `_write_dir_entry`'s frame postconditions is driven by the **full-module program
apparatus** (the abstract self-call stubs + 60 sibling `let` bodies), *not* the cited axiom set — and
that narrowing axioms does **not** help; only a (still-unbuilt) Why3 `scope` boundary that prunes the
program apparatus would. The read trio lives in the **same module** with the **same apparatus**, so the
value marker — even though it fires exactly once and is logically clean — may red the full gate for the
same apparatus-feasibility reason. **The spike (§7) is precisely the cheapest probe of this risk.**

**Secondary risk:** the body lever (§3.3). The read body reads through `Array.sub` + opaque
`_unpack_direntry`; surfacing the literal byte terms for the marker intro requires a faithful body
restructure that the write side only managed with a `#@ sibling_concrete` byte helper. If the read
restructure cannot surface the bytes without re-exploding the loop invariant, the marker intro never
fires.

**Cheaper alternatives:**
- **Keep the 3 read-side `dirscan-fidelity` trusts as logged GAPs** (the current banked state, PR #44).
  Honest, zero-risk, already in the tree. This stays the correct default until the spike greens.
- **The `fd-resolution-fidelity` trust** (`sys_open`, `:1556`) is NOT obviously the better next target:
  SKILL.md A.14 records that de-trusting `sys_open`'s fd-resolution leaves **11 unproven goals** whose
  core is "the `dir_lookup` resolution `<==>` + fd→inode binding non-derivable across the `no_inline`
  opaque name-scan — **the dirscan-fidelity class**." In other words, retiring `fd-resolution` likely
  **depends on** the very `dir_lookup`-correspondence this proposal designs. So the read-side dirscan
  work is plausibly **upstream** of the fd-resolution retirement, not a competing alternative.

**Recommendation:** **SPIKE-FIRST (Milestone-0, §7).** The design is sound and the write-side blueprint
is directly transferable, so this is not a "keep-as-GAP forever" — but the dominant risk (the A.7
apparatus-feasibility wall that *defeated the write side's analogous final step*) is real enough that a
human should **not** authorize the full build until the bounded full-gate spike demonstrates the
marker-keyed value axiom actually discharges `_dir_lookup`'s fidelity ensures in-module. If the spike
reds with the apparatus explosion, the doctrine-correct outcome is to **keep the trio as logged GAPs**
and route the *module-scope-emission feature* (shared with the write side) to the human as the real
prerequisite — at which point read + write dirscan retire together.

---

## Appendix — evidence index (file:line)

- Read-side trio + fidelity ensures: `pure_lib/os/UnixInodeFileSystem.py:972` (`_dir_lookup`),
  `:1024` (`_dir_find_slot`, `slot_name == pathname`), `:1054` (`_dir_find_free`); body loop
  `:974-986`.
- `dir_lookup` relational axioms (no value form): `src/pycsl/module6_whyml/preamble.py:123-131`
  (`scan_reflects_present`, sign-IFF), `:171-176` (witness), `:195-204` (present_zero_frame),
  `:343-351` (`remove_reflects_absent`), `:762-768` (`dir_lookup_frame`, between-states `=`).
- Uninterpreted backing symbols: `preamble.py:1212-1214`.
- Gap-9 existential-explosion rationale (why value form omitted): `preamble.py:109-122`, `:150-161`.
- Kernel scan Fixpoint (computes the value) + `dir_lookup := scan ... 16 (-1)`:
  `unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixDirScan.v:50-62`, `:131`; sign-only theorem
  `:134-138`; NO value lemma (grep confirms).
- Name codec ENCODE direction: `preamble.py:942-950` (`field_to_str_round_trip`, exhibit
  `0708.proofs/`), `:986-991` (`field_to_str_frame`, `0714.proofs/`), `:321-324`
  (`slot_name_byte_decode`, `0712.proofs/`). RECOVER direction: unmodeled (GAP doc §3b).
- Write-side marker blueprint (the transferable precedent): `preamble.py:506-555`
  (`dir_blit_marker_intro`, definitional/zero-trust), `:668-672` (`dir_blit_marker_value_inode`),
  `:730-734` (`dir_blit_marker_at_value_name`, RECOVER-direction name via kernel), `:739-746`
  (`frame_only`); body cites `UnixInodeFileSystem.py:1130-1135`, asserted atom `:1177`; exhibits
  `0716.proofs/` / `0718.proofs/`.
- Landed write-side retirements: `git log` `4308cd6` (7→6), `6db50b9` (6→5), `03006a1` (5→4); GAP
  banked `a00e2b6` (#44).
- A.7 apparatus-feasibility wall (the biggest risk, write-side evidence):
  `config/skills/pycsl-monitoring/SKILL.md` §B (rows "marker fires EXACTLY ONCE … BUT the FULL body
  gate STILL reds" and "A.7 too-many-axioms diagnosis REFUTED");
  `getting-better/20260619-0905-write-dir-entry-7to6-modulesplit-GAP.md`.
- fd-resolution depends on dirscan: SKILL.md A.14 ("11 unproven goals … the dirscan-fidelity class").
