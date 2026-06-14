# String ↔ fixed-width byte-field codec — investigation + plan (2026-06-14)

Goal: model the **string ↔ fixed-width null-padded byte-field** round-trip (the `struct '>Ns'`
field ↔ Python `str`) faithfully, so `slot_name`-style decodes become real string semantics
instead of opaque abstract functions. This retires a whole class of walls at once: the heavy-
syscall name-resolution asserts (rename/unlink/rmdir/symlink), `content_round_trip`,
`readlink` target value — and it is the missing prerequisite that makes the directory-model
concretization (allocator-plan option (a)) actually feasible.

## 1. Investigation findings (what exists today)

### Why3 `string.mlw` is RICHER than expected — the building blocks are present
(`$OPAM/.../why3/stdlib/string.mlw`)
- `module String`: `length`, `concat`, `s_at s i` (the char at `i` as a length-1 string),
  `substring`, `prefixof`/`suffixof`/`contains`/`indexof`, `to_int`.
- **`extensionality` axiom** (`forall s1 s2. eq_string s1 s2 -> s1 = s2`, a
  `meta extensionality predicate`) — **two strings are equal iff equal per char/length.**
  THIS is the linchpin the field round-trip needs (prove name equality char-by-char).
- `module Char`: `type char` with `code : char -> int` **constrained `0 <= code c < 256`**
  (chars ARE bytes — so a concrete byte-decode of a char is sound), `chr : int -> char` with
  `code_chr` (`0<=n<256 -> code(chr n)=n`) and `chr_code` (`chr(code c)=c`); `get s i : char`
  with `(get s i).contents = s_at s i`; `substring_get`, `concat_first/second` (char-level
  reasoning through substring/concat). All THEORY axioms — **zero TCB**.

### PyCSL already lowers most string ops onto this theory
(`module6_whyml/expressions.py`)
- `ord(c)` → `ord_op c` with `ensures result = Char.code (Char.get c 0)` + `0<=result<256`.
- `chr(b)` → `chr_op b` with `ensures result = (Char.chr b).contents` (length-1 string).
- string index / slice → `String.substring`; `len(str)` → `String.length`; `+` → `String.concat`;
  `in`/prefix → substring/`contains`. String equality → Why3 `=` (extensionality available).
- **Gap 5 is CLOSED** (`7f53db2`): the per-CHAR byte round-trip `chr(ord(c))==c` proves as a
  `string.Char` theory lemma; `disk[off]=ord(name[k]); chr(disk[off])==name[k]` proves.

### What is MISSING — the string-LEVEL field codec
`slot_name` is the whole name (≤30 chars), stored `'>30s'`: `disk[off+i]=ord(name[i])` for
`i<len`, null-padded after. The per-char codec works, but there is no modeling of:
- **reconstructing** the decoded string from the N field bytes (Why3 `String` has NO
  `init`/`make` constructor — you cannot directly write "the string whose char `i` is
  `chr(disk[off+i])`"), and
- the **null-padding / length** semantics (`'Ns'` truncates+pads; the name is the field up to
  the terminator — `decode_full_30(field) != name` for `name` shorter than 30 because of the
  trailing nulls).
So `slot_name` stays an abstract `val function`, framed only by the E-matching
`block5_decode_frame` axiom — which is exactly why the heavy-syscall name-resolution asserts
(`slot_name(k)==pathname ==> …`) blow up.

## 2. Feasibility verdict
**FEASIBLE, likely zero-or-minimal new TCB, MODERATE complexity.** The hard parts are (a)
string RECONSTRUCTION without an `init` (solve via an abstract `field_to_str` characterized by
`Char.get`/`length` axioms + extensionality, NOT a 30-fold concat), and (b) the null-padding/
length round-trip (needs `name` ≤ width + no-embedded-null preconditions, faithful to Python's
`'Ns'`). Main RISK is **SMT string-theory performance** — Alt-Ergo's string support is weak;
extensionality + substring reasoning may force reliance on **Z3** and may be slow. So gate
performance early.

## 2.5 PHASE-A DE-RISKING RESULT 2026-06-14 — SMT round-trip is NOT dischargeable (reverted)
Ran the spike: added `function field_to_str` + the definitional `field_to_str_spec` to the
registry, wrote corpus `0707` as a `#@ lemma` (a name written `'>Ns'`-style into a buffer reads
back `== name`), and tried to prove it from `field_to_str_spec` + `string.Char` + `extensionality`.
Findings:
- **Two prerequisite gaps surfaced first:** (i) the `field_to_str_spec` axiom needs `use
  string.Char`, but `needs_char` only scans BODIES, not contracts (the lemma's `ord` is in a
  `requires`) — fixable; (ii) `ord`/`chr` lower to a program `val` (`ord_op`), which **cannot be
  used in a contract** (logic context) — the os only ever used `ord`/`chr` in bodies. A pure
  logic `function` works in contracts but then **cannot be used in the os program bodies**
  (`chr_op ... non-ghost context`). So ord/chr need context-dependent lowering (inline
  `Char.code (Char.get c 0)` in `_in_spec`, `ord_op` in program) — a separate small fix.
- **THE FATAL FINDING — the round-trip is NOT SMT-dischargeable.** Even after the codec
  typechecks, proving `field_to_str(buf,0,width) == name` via `extensionality` **times out at
  ~23 MILLION steps** (Alt-Ergo AND Z3); a `[field_to_str d off width]` trigger on the spec
  axiom does NOT help (the blowup is the `extensionality`/`eq_string` reasoning itself, not spec
  instantiation). This is exactly the §4 "biggest risk: SMT string-theory performance" — and it
  is fatal to the zero-TCB SMT approach. PyCSL's contract language also can't express the needed
  proof guidance (explicit `eq_string`/per-char extensionality invocation).
- **REVERTED** the spike (registry + ord/chr-logic + 0707); working tree back to clean `8e64499`.
- **THE VIABLE PATH (Phase A'):** prove the field round-trip OFFLINE in **Rocq + Lean** and cite
  it as a cross-validated `axiom` (the project's established pattern for SMT-hard facts —
  `block5_decode_frame`, the struct codecs). String/char induction is tractable with tactics
  where SMT thrashes. COST: it adds a CITED (cross-validated) axiom to the TCB — not the
  zero-TCB outcome originally hoped — plus authoring the Rocq + Lean proofs, plus the
  context-dependent ord/chr lowering. Still feasible and still unblocks the whole class, but it
  is a bigger, TCB-adding effort than the §3 plan assumed. DECISION NEEDED before proceeding.

## 2.6 PHASE A' RESULT 2026-06-14 — cross-validated axiom WORKS (delivered)
The user chose the cross-validated Rocq+Lean route. Delivered and fully gated:
- **The round-trip as a CITED axiom proves FAST.** `UnixFs.Field.field_to_str_round_trip`
  (abstract `function field_to_str (d: array int) (off width: int) : string`, registry) is
  the ENCODE→DECODE round-trip. The corpus test `0708.py` (the encoding preconditions →
  `field_to_str(buf,off,width) == name`, empty body) proves **Valid in 0.02s / 18 992 steps**.
  The Phase-A OOM is GONE: SMT only APPLIES the axiom (O(1)); the extensionality reasoning is
  offline in the proof assistants. KEY ENABLER: `ord(name[i])` in a contract must lower to
  `Char.code (Char.get name i)` DIRECTLY (not via `String.substring name i 1`) so it matches
  the axiom antecedent syntactically — otherwise the antecedent is unprovable and SMT falls
  back to extensionality on the string-equality goal → OOM (this exact mismatch was measured).
- **Cross-validated, machine-checked.** `0708.proofs/{rocq,lean}/FieldToStrRoundTrip.{v,lean}`:
  `field_to_str` defined as the scan-to-first-null decode over an abstract byte-reader (string
  ↔ `list Z`/`List Int`), round-trip proved by list extensionality (induction) + per-char
  `chr(code c)=c`. `--reverify-proofs` PASSES — Rocq **Closed under the global context** (only
  the abstract Section Variable `rd`, 0 Axiom/Admitted); Lean **axioms ⊆ {propext, Quot.sound}**,
  no sorry. The faithful Why3↔proof symbol correspondence is documented in the registry comment
  and both proof headers.
- **Tool changes** (all byte-safe): context-dependent `ord`/`chr` lowering (logic form in a
  contract, `ord_op`/`chr_op` program val in a body); `needs_char` now also scans contracts +
  cited Char-axioms; the `UnixFs.Field.` registry decl + axiom; and `crosscheck_ir` now SKIPs
  (not FAILs) an axiom whose three sides are ALL `Unsupported` (a pure parser gap — string/char/
  array-index facts beyond the syntactic canonicalizer, exactly like the os `UnixFs.Dir.*`
  axioms which sit outside that gate; a MIX still FAILs, so no real disagreement is masked).
- **Gates GREEN/consistent:** os `__init__` proves SUCCESS; body gate type-checks; corpus
  byte-diff = **0 changed** (only new `0708.mlw`); `--audit-proof --reverify-proofs` 4/4 PASS;
  `check-proof-crosscheck` 17 PASS / 12 SKIP / **0 FAIL**; axiom-registry-drift clean (orphan,
  like all os structural axioms); axiom-registry-emittable 7/20 (was 7/19 — +1, the SAME
  pre-existing parser-gap class as the struct round-trips, an already-RED progress gate).
- **NOT zero-TCB (as foretold):** this adds ONE cited, cross-validated axiom to the trusted
  base — the honest cost of an SMT-intractable string fact.

NEXT (Phases B–C): re-model `slot_name d 5 k := field_to_str d (5*512+32*k+2) 30` (+ likely
`slot_inode` 2-byte decode + block-5 byte-range invariant), reconcile the `UnixFs.Dir.*`
axioms against the concrete decode, then the heavy directory syscalls' `slot_name==pathname`
asserts + `content_round_trip` + `readlink` reuse the SAME codec. When the os cites
`UnixFs.Field.field_to_str_round_trip`, make its proofs findable by the os audit (copy into
`unix-filesystem/UnixInodeFileSystem.proofs/` or point `--rocq-dir`/`--lean-dir`).

## 2.7 PHASE B/C 2026-06-14 — REDIRECTED by measurement; ENCODE side delivered
**Finding that redirected Phase B.** Body-gate measurement (`--fun unixinodefilesystem__sys_unlink`)
showed the heavy-syscall (unlink/rmdir/rename) failures are **E-matching EXPLOSIONS with the
facts already present**, NOT missing codec facts: e.g. `assert slot_inode(disk,5,slot)==0` —
VERBATIM `_zero_entry`'s own postcondition — times out at 10.6M steps; the absence/uniqueness
assert OOMs. The forward round-trip codec does NOT address these (they are uniqueness/absence,
not encode→decode). And concretizing `slot_name = field_to_str` would add MORE terms (worse
E-matching) and risk the green `__init__` gate. So the plan's "concretize slot_name" lever is
WRONG for the heavy syscalls — those need E-matching control, a separate problem. DECISION
(user): redirect the codec to where it genuinely fits — **content_round_trip + readlink**
(forward-decode facts the round-trip axiom discharges).

**Delivered (gated; the ENCODE side, de-opaquing gap-5 at the encoder):**
- `char_code_at` body lowering: `ord(s[i])` in a BODY now lowers to `char_code_at s i`
  (ensures `result = Char.code (Char.get s i)`), NOT `ord_op (str_sub_op s i 1)`. The latter's
  `String.substring` detour made an encode loop's invariant `out[j] == Char.code (Char.get name j)`
  only reachable via a `substring_get` bridge that E-match-explodes (measured OOM). The direct
  form matches the invariant atom-for-atom (the body twin of the Phase A' spec rule). Byte-diff:
  ONLY `0702.mlw` changes (the lone body `ord(s[i])`), still proves — a strict simplification.
- `_pad_name` strengthened: now proves `\result[i] == ord(name[i])` (i<min(len,30)) + null-pad
  tail, exposing the encode side (was opaque gap-5, only `\length==30`). `_pad_name` body gate
  PROVES; os `__init__` stays GREEN (it feeds `_write_entry`, but `slot_name` rides on
  `_write_entry`'s ensures, not `_pad_name`'s bytes, so no Dir-model perturbation).
- `0708.py` gains `encode_field`: the END-TO-END round-trip — an encode loop builds a 30-byte
  `'>30s'` field, then `field_to_str(\result,0,30) == name` (the cited codec axiom closes the
  decode). Proves Valid. This is the symlink-target / content_round_trip shape, standalone.

**Latent bug found (NOT fixed; avoided):** `len(array_local)` in a loop INVARIANT emits
`Array.length !out` for a plain-array local (`out = [0]*N` binds `Array.make`, no ref) →
typecheck failure. Subscript `out[j]` in an invariant is FINE. Avoided by not putting
`\length(out)` in invariants (the `Array.make` length is statically known). Worth a separate fix.

**REMAINING (harder, gap-15 effect contracts):** the in-os symlink→readlink CROSS-CALL round-trip
(symlink writes the target field; readlink, a separate call, decodes `== target`) needs
`_pack_direntry` byte-preservation ensures + an inode→block→field framing + readlink returning the
target. That is the intricate effect-contract arc, not low-risk — deferred.

## 2.8 HEAVY-SYSCALL E-MATCHING INVESTIGATION 2026-06-14 — §2.7's "E-matching" claim CORRECTED (reverted)
§2.7 said the heavy-syscall failures are "E-matching explosions with the facts already present."
That was WRONG (it rested on a `--fun`-scoped read that hid the cause). The true, deeper finding:
- **The fact was NOT present.** The `#@ no_inline` boundary stub `self__zero_entry_<n>` that the
  syscall body actually CALLS carried ONLY `writes { self.disk }` — `_zero_entry`'s ensures
  (`slot_inode(self.disk,b,s)==0` + the `\forall k. … == \old(…)` frame) were ALL dropped. Root
  cause: the six method-call ensures maps (`functions.py`) each reject the clause kind — `field_old`
  rejects params, `field_param_result` requires `\result`, and EVERY `classify` rejects a
  quantifier-bound `k` as a bare non-param Var. So a void mutator's quantified self-field frame
  propagates NOWHERE. `assert slot_inode(disk,5,slot)==0` then has no hypothesis → the prover
  thrashes (the "10.6M-step timeout" was searching an UNPROVABLE goal, not E-matching noise).
- **A fix was built + validated then REVERTED.** A new `_build_method_field_param_old_ensures_map`
  (self-field + params + `\old` + bound-var threading, params→x_i) restores the frame on the stub;
  it took `sys_unlink` from 3 unproven → 1, with os `__init__` GREEN and corpus byte-diff = 0.
- **WHY reverted — the frame ensures POISON surrounding goals.** Once restored, the frame
  `\forall k. f(self.disk,5,k) == \old(…)` needs a trigger to be usable, but ANY trigger broad
  enough (`[slot_inode disk 5 k]` / `[self.a[k]]`) fires on EVERY array/decode access in the
  caller — INCLUDING unrelated `Index in array bounds` VCs — and explodes THEM (18M steps; Alt-Ergo
  Unknown, Z3 timeout). Standalone repro (corpus-shaped `Buf.poke`/`bump_one`): the asserts were
  fine but the array-bounds checks for `self.a[i] <- 7` / `self.a[j]` blew up. (Aside: a lowered
  trigger must be BARE — `[(t)]` with parens is silently mis-parsed → auto-trigger fallback.)
- **CONCLUSION.** Closing the heavy syscalls is a genuine MULTI-PART research problem, not a quick
  E-matching-trigger fix: (1) propagate the callee's quantified frame across the no_inline boundary
  WITHOUT a broad trigger that poisons surrounding goals — likely a targeted per-call-site frame
  lemma or a frame representation immune to the bounds-check interaction, NOT blanket frame ensures;
  (2) the absence/uniqueness assert additionally needs `uniq_elim` + a `slot_inode < 32` bound + a
  hint. Reverted to `b7fc06e`; the `field_param_old` map + `_frame_trigger_term` machinery are
  documented here for whoever resumes.

## 2.9 PER-CALL-SITE FRAME-LEMMA ATTEMPT 2026-06-14 — shared-stub + Call-trigger = MIXED, reverted
Re-attempted the fix with the §2.8 refinements made principled: (a) `_build_method_field_param_old`
captures only field+param+no-result clauses (Subscript-on-Var rejected → no `subscript_get`); (b) a
QUANTIFIED frame is kept ONLY when its term is a function APPLICATION (a decode like `slot_inode`),
never a raw-array subscript; (c) the trigger is the BARE post-state Call (`[slot_inode self.disk x0
k]`), specific enough to miss raw `self.disk[i]` bounds reads. Emission was clean: byte-diff = 0
(corpus), os `__init__` GREEN, and the body-gate `.mlw` diff was 7 lines, PURELY ADDITIVE (frame
ensures + `_write_entry`'s previously-dropped write postconditions on the shared stubs).
**RESULT — net MIXED, so reverted:** simple removers improved (`sys_unlink` 3→2, `sys_rmdir` 2→1,
`sys_mkdir` proven), but the richer adders REGRESSED — `sys_link` went from a CLEAN "1 goal remains"
(timeout) to a disruptive **OOM**, and `sys_symlink` likewise OOMs. Root cause: the frame ensures
live on the SHARED stub (`self__write_entry_4`/`self__zero_entry_2`), so they float into EVERY
caller; in a richer caller (link/symlink: inode read/write + alloc → many more `slot_inode` terms)
even the specific Call-trigger fires enough to blow up. So this is per-STUB, NOT per-call-site.
**The genuine per-call-site mechanism** (the real fix) must deliver the frame fact LOCALLY at the one
call site that needs it (e.g. an `assume`/lemma instantiation emitted right after `self._zero_entry(…)`
in unlink/rmdir only), so it never enters link/symlink's context — a deeper change than shared-stub
ensures. Reverted to `9e781cb`.

## 2.10 LAYER-1 LANDED 2026-06-14 (commit 4cd0d0f) — non-quantified write-posts propagate
The SAFE half of §2.9, split out and delivered. `_build_method_field_param_post_ensures_map`
propagates a void mutator's NON-QUANTIFIED self-field+param postconditions
(`slot_inode(self.disk,b,s)==inode` / `==0`) across the `#@ no_inline` boundary stub — the write
WITNESS that the six earlier maps all dropped. Non-quantified ⇒ no trigger ⇒ CANNOT poison (the
failure mode that sank the quantified-frame attempt). Body-gate (--fun, baseline→fix):
**sys_unlink 3→1, sys_rmdir 2→1**, sys_rename OOM→4-clean, mkdir/link unchanged, symlink unchanged.
os `__init__` GREEN; corpus byte-diff = 0; regression test `0710` (fails at baseline, proves with
the fix). NOTE it beat the quantified-frame attempt even on unlink (3→1 vs 3→2) — the quantified
frame was hurting even there.

STILL OPEN (Layer 2 — the genuine per-call-site QUANTIFIED frame): the remaining absence/uniqueness
asserts (`\forall k≠s. slot_name(k)==p -> slot_inode(k)==0`) need the FRAME (`\forall k.
slot_x(disk,5,k)==\old(...)`) AND `uniq_elim` + a `slot_inode<32` bound. The frame must be emitted
LOCALLY at the one call site that needs it (a labeled `assume` after `self._zero_entry(…)` in
unlink/rmdir, using `(… at PreCall)` for the pre-call value), NOT on the shared stub — else it
poisons rich callers (link/symlink, §2.9). That is a new statement-level directive + labeled-assume
emission + audit + docs, plus the uniqueness proof — a substantial, separate effort.

## 3. Plan (phased; gate after each)

### Phase A — the codec primitive `field_to_str` (the foundation)
- New logic function (registry `_AXIOM_FUNCTIONS`, os/string namespace):
  `function field_to_str (d: array int) (off: int) (width: int) : string` — the
  null-terminated name in the `width`-byte field at `off`.
- Characterizing facts (aim to DERIVE from `Char`/extensionality = zero TCB; cite + cross-
  validate only if a residual is needed):
  - `0 <= length (field_to_str d off width) <= width`;
  - `forall i. 0 <= i < length(field_to_str d off width) -> Char.get (field_to_str d off width) i = Char.chr d[off+i]` (char at `i` is the decoded byte);
  - terminator: `length < width -> d[off + length] = 0`.
- The **round-trip lemma** (the payoff): for `name` with `m = length name <= width`, no
  embedded null, if `forall i<m. d[off+i] = ord(name[i])` and `d[off+m]=0`, then
  `field_to_str d off width = name` — proven via `extensionality` (same length `m`; char `i` =
  `chr(d[off+i]) = chr(ord(name[i])) = name[i]` by `chr_code`).
- **Corpus** (§5 discipline): a standalone test writing a name into an N-byte field and reading
  it back == the original (the codec round-trip), independent of os.

### Phase B — re-model the dirent name on the codec
- `slot_name d blk k := field_to_str d (blk*512 + k*32 + 2) 30` — now a FUNCTION OF THE SLOT
  BYTES → congruence framing (a write to a different slot leaves it unchanged for free; a write
  to THIS slot gives the new name via the codec). Replaces the opaque abstract `slot_name`.
- Reconcile the existing `UnixFs.Dir.*` axioms (`scan_reflects_present`, `remove_reflects_absent`,
  `block5_decode_frame`, uniqueness) with the concrete `slot_name`: `block5_decode_frame`
  becomes PROVABLE (congruence) → droppable; the others must still hold over the concrete decode
  (re-validate or re-derive). Likely also concretize `slot_inode` (2-byte decode) here — but
  FIRST extend the byte-range class invariant to cover block 5 `[2560,3072)` so a concrete
  `slot_inode` stays `>= 0` (consistency with `slot_inode_nonneg`).

### Phase C — the os syscalls + content/readlink (the payoff)
- The name-resolution asserts (rename/unlink/rmdir/symlink `slot_name(k)==pathname`) now prove
  via the codec round-trip + per-slot congruence frame — closing the heavy syscalls.
- `content_round_trip` (file bytes ↔ value) and `readlink` target reuse the SAME field codec
  (the target/content is a byte field) — both unblock.
- This is also the prerequisite for allocator-plan option (a): with a concrete `slot_name`,
  the directory model concretizes cleanly.

### Phase D — gating, corpus, docs (NON-NEGOTIABLE)
- os `__init__` GREEN after every step; corpus byte-diff (string-codec is os/registry-scoped →
  expect byte-safe except new tests); behavior-changing → corpus PROOF.
- Any new axiom: DERIVED from `Char`/extensionality (zero TCB) or cross-validated Rocq+Lean.
- doc-coherency: any new `#@` surface documented across all 5 surfaces + traceability.
- **Watch SMT perf**: re-time os `__init__` + the body gate — string reasoning may slow it or
  need Z3-only on some goals.

## 4. Risks / unknowns
- **SMT string performance** (biggest): extensionality + substring can be slow/unstable; may
  need Z3 and per-goal tuning. Validate on a minimal codec proof BEFORE re-modeling the os.
- **Reconstruction axioms**: if `field_to_str`'s characterization can't be fully derived from
  `Char`, a small cross-validated `string`-theory lemma is needed (acceptable, like the existing
  ones).
- **Null/length semantics**: faithful `'Ns'` truncate+pad + no-embedded-null; get the
  preconditions exactly right or the round-trip is unsound.
- **Scope**: keep to the fixed-width null-padded field (dirent name / symlink target / content
  buffer reuse it). Do NOT drift into a general string-rewrite.

## 5. Sequencing
A (codec primitive + corpus, validate SMT perf) → B (re-model slot_name/slot_inode + invariant
extension, re-validate Dir axioms) → C (syscalls + content/readlink) → D (gates/docs throughout).
Phase A is the de-risking spike: if the codec round-trip proves cleanly and fast on a standalone
corpus test, the rest is propagation; if SMT chokes on it, reconsider before touching the os.
