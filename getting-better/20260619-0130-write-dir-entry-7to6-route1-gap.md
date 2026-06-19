# `_write_dir_entry` 7→6 retirement — ROUTE 1 (unique marker atom): GAP (poison eliminated, aggregate-context wall remains)

DATE: 2026-06-19
LOOP: test-supervise-sl (mission: route 1 — narrow the folded maintenance axiom's trigger
so it fires EXACTLY ONCE at the genuine apply site, via the gap-17 `block_content_eq`
unique-marker-atom discipline; then assemble the `_write_dir_entry` 7→6 retirement. STOP
AT THE PROPOSAL.)
STATUS: **DOES NOT RETIRE — but route 1 SUCCEEDS at its stated job.** The unique-marker
trigger ELIMINATES the trigger-poison wall (the original blocker): the sibling byte helper
`_blit_dir_entry` is now CLEAN (8.6e9-step Timeout → SUCCESS), and `_write_dir_entry`
itself PROVES in `--fun` isolation (real, soundness-probe-clean, falsification-confirmed
non-vacuous). The marker intro/insert are CROSS-VALIDATED zero-TCB in BOTH provers. BUT the
de-trust still REDS the FULL body gate: `_write_dir_entry`'s marker-discharge OOMs/Timeouts
in the full module (catalog-B A.7 aggregate-context E-matching pollution) — it proves alone
but not co-located with the rest of the os axiom web. Per doctrine, a de-trust that reds the
full body gate is a REGRESSION, not a retirement → **logged GAP routed to the human.** Tree
reverted to clean HEAD; the reproducible v2 patch + cross-validated proof sources captured.

## Bottom line (the mission questions)
1. **Does it NOW retire 7→6 with both gates green + soundness probe clean? NO.** The
   `#@ \trusted reviewer: dirscan-fidelity` on `_write_dir_entry` is removed (count 7→6
   syntactically — and it WOULD be the first dirscan-fidelity retirement), but the FULL body
   gate reds (baseline 2 → 3, +1 NEW unproven = `_write_dir_entry` aggregate-context wall;
   the other 2 are the pre-existing `sys_rename` baseline noise). Not ≤ baseline → REGRESSION.
2. **Did route 1 do its job (fire EXACTLY ONCE, eliminate the poison)? YES.** The marker
   trigger keeps the maintenance axiom OUT of `_blit_dir_entry` and every other block-5 byte
   mutator. `_blit_dir_entry`'s pure-byte postcondition went from **Timeout 8,605,711,403
   steps** (the documented poison) to **SUCCESS, 0 non-Valid**. The poison did NOT relocate.
3. **Is the marker cross-validated zero-TCB? YES (both provers).** See below.
4. **The precise residual (NEW, narrower than the original proposal):** with the byte-decode/
   string keystones NO LONGER cited (the marker carries both slot VALUE decodes), the only
   remaining wall is `_write_dir_entry`'s marker-discharge under the FULL module's shared
   E-matching context — it proves in `--fun` but OOMs in the full file. This is catalog-B
   pattern A.7 (context pollution), NOT trigger-poison, NOT vacuity, NOT a logic gap.

## The route-1 marker design (the eligible, cross-validated deliverable)

A UNIQUE uninterpreted predicate keyed on a marker atom (the gap-17 `block_content_eq`
discipline), declared in `_AXIOM_FUNCTIONS["UnixFs.Dir."]`:

```
predicate dir_blit_marker (d0 d1: array int) (s b0 b1: int) (name: string)
```

Three registry axioms, ALL triggered `[dir_blit_marker d0 d1 s b0 b1 name]` — so the
maintenance step fires ONLY where the mutator body asserts the marker, NEVER on a raw
`disk[2560+<expr>]` byte read:

- `dir_blit_marker_intro` (DEFINITIONAL, zero trust): the marker is conservatively DEFINED as
  the conjunction of ALL byte facts a blit at slot s establishes (the two inode bytes, the
  per-char name-field bytes, the null-pad, the byte-region frame) PLUS the name
  well-formedness the round-trip needs (len<=30, no embedded null). One direction of the iff
  `marker <-> bytes`.
- `dir_blit_marker_insert` (cross-validated): from the marker + uniq/slots_lt32 d0 + inode
  range + freshness, conclude BOTH slot VALUE decodes (slot_inode = 256*b0+b1 AND slot_name =
  name), the slot-locality frame (∀k≠s), uniq d1, slots_lt32 d1 — in ONE marker-keyed step.

**The key route-1 move that eliminated the poison:** fold the NAME value into the marker
conclusion too, so `_write_dir_entry` cites ONLY the marker axioms (intro + insert) and the
read-side scan facts — and does NOT cite `slot_inode_byte_decode` / `slot_name_byte_decode` /
`field_to_str_round_trip`. Those byte/string keystones key on the GENERIC shape
`disk[blk*512+32*k]` / `field_to_str`, so citing them EMITS them module-wide and their
triggers E-match-explode any sibling byte loop. With them un-cited (and un-emitted), the
string round-trip is discharged entirely INSIDE the kernel proof, behind the marker — no
byte-decode/string keystone exists in the module to poison `_blit_dir_entry`.

`_blit_dir_entry` was also rewritten to write the 32-byte dirent DIRECTLY into `self.dir`
(2 inode bytes + a single 30-byte name loop) instead of composing
`_pad_name`+`_pack_direntry`+`Array.blit`; that 3-stage array-transform chain made the
per-byte name ensures explode even without any keystone. `_pad_name` gained the top-level
byte-VALUE ensures (its loop invariants already proved them).

### Cross-validation outputs (verbatim, this run)
Sources: `test-suite/corpus/pycsl-reference/0716.proofs/{rocq,lean}/DirBlitMarker.{v,lean}`.

```
# Rocq 8.20.x — Print Assumptions (both theorems): Section Variables only
Section Variables:
rd    : disk -> Z -> Z
nlen  : name_t -> Z
nchar : name_t -> Z -> Z
name_t : Type
disk   : Type
# (Closed under the global context; 0 Axiom/Admitted.)

# Lean 4 — #print axioms:
'UnixFs.Dir.dir_blit_marker_intro' does not depend on any axioms
'UnixFs.Dir.dir_blit_marker_insert' depends on axioms: [propext, Quot.sound]
```

The kernel models `name` as a char-code list (`name_t`/`nchar`/`nlen`), and the name value as
`name_val nm` — the SAME faithful interpretation as the already-banked `field_to_str_round_trip`
(0708). The marker is DEFINED as its byte hypotheses, so `dir_blit_marker_intro` is
`fun h => h` (definitional) and `dir_blit_marker_insert` is the byte-rung blit theorem (0715
DirBlitInvariant) with the name round-trip (FieldToStrRoundTrip model) added — same proof,
zero new TCB. `scan_recovers` (the byte→name round-trip) and `slot_frame_of_region` (the
byte-region→slot frame bridge) are proved once and applied opaquely.

## Gate evidence (authoritative full body gate, PYTHONHASHSEED=0, best-of-N Alt-Ergo+Z3)

- **BASELINE (clean HEAD, `_write_dir_entry` trusted): 2 goals remain** — both
  `sys_rename` Assertion Timeout (4,621,194 / 247,639 steps), pre-existing baseline noise.
  (`_unpack_direntry` happened to prove this run; aggregate noise is non-deterministic.)
  0 affected `\trusted`; `_write_dir_entry` trusted.

- **Per-method probes (de-trusted, `--fun`):**
  - `_pad_name` (new top-level value ensures): **SUCCESS.**
  - `_blit_dir_entry` (pure-byte helper): **SUCCESS, 0 non-Valid** — was Timeout
    **8,605,711,403 steps** in the v1 inode-only marker (the relocated poison). The
    unique-marker trigger + direct-write helper ELIMINATE it.
  - `_write_dir_entry` (the de-trusted target): **SUCCESS, 0 non-Valid** — the marker
    discharges value(inode+name)+frame+uniq+slots_lt32.
  - **Falsification probe** (body blits to wrong slot `entry_offset+32`):
    `_write_dir_entry` postcondition correctly **FAILS** (4 goals) → the `--fun` pass is a
    REAL proof, non-vacuous.
  - **Soundness probe** (`#@ requires slot_inode(self.dir,5,0)==3`, a non-canonical
    populated disk): `_write_dir_entry` **still SUCCESS** → NOT an empty-disk artifact.

- **FULL body gate (de-trusted): 3 goals remain** — `_write_dir_entry` Postcondition ×2
  (OOM 9.19s + Timeout 5,461,435 steps) + `sys_rename` ×1 (baseline). Adding explicit
  conclusion-pinning asserts (v3) relocated the failure from Postcondition to the asserts
  themselves (OOM 16.68s + Timeout 5,461,435 / 253,385) — same 3-goal count. So
  `_write_dir_entry` proves alone but NOT in the full module: **catalog-B A.7 aggregate-context
  E-matching pollution** — the os axiom web (scan_reflects_present / remove_* / dir_lookup_frame
  / establish_* / the marker axioms) starves the marker-discharge's step budget.

- **`\trusted` count:** HEAD os = **7**; de-trusted working tree = **6** (the
  `_write_dir_entry` dirscan-fidelity directive removed). Would be the FIRST dirscan-fidelity
  retirement — but the body reds, so it does NOT retire.

- **`__init__` gate + full-corpus byte-diff:** NOT run to completion — the body gate already
  fails decisively (the retirement is dead at the body gate). The marker axioms are
  emission-gated (UNCITED ⇒ corpus byte-diff 0; the byte-decode/string keystones are NO
  LONGER cited at all, so they are absent from the os `.mlw` in this attempt).

## What route 1 changed vs the prior proposal (20260618-2350)

| | Prior proposal (byte-keyed fold) | Route 1 (unique marker) |
|---|---|---|
| Trigger | `[d1[2560+32*s]]` (matches every block-5 byte read) | `[dir_blit_marker d0 d1 s b0 b1 name]` (matches ONLY the asserted atom) |
| `_blit_dir_entry` | Timeout **8.6e9 steps** (poison relocated here) | **SUCCESS** (poison eliminated) |
| byte-decode/string keystones | cited at `_write_dir_entry` → emitted module-wide → poison | NOT cited; name value folded into the marker, discharged in-kernel |
| `_write_dir_entry` in `--fun` | OOM | **SUCCESS** (soundness-probe clean, falsification-confirmed) |
| FULL body gate | 3 (+2 new explosive) | 3 (+1 new: `_write_dir_entry` aggregate-context wall) |
| Residual class | trigger-poison (sibling mutator) | aggregate-context pollution (A.7, the genuine site) |

Route 1 did EXACTLY what the mission asked — fire once, kill the poison — and surfaced a
DEEPER, narrower wall: the marker-discharge is sound and proves in isolation but cannot
survive the full module's shared E-matching context.

## The precise residual / what a future session needs (NOT autonomous — human-gated)

The marker logic is correct (cross-validated) and the proof is REAL (non-vacuous, soundness
clean). The remaining engineering is purely about the FULL-MODULE step budget for the
marker-discharge VC. Candidate directions (each a tooling/TCB decision, none a `\trusted`):
- **Split the module** so `_write_dir_entry` (and the dir mutators) verify against a SMALLER
  axiom set — the A.7 remedy (pattern A.7 / catalog-B). The os file co-locates the marker
  axioms with the whole dir/inode/content axiom web; isolating the dir-mutator VCs from the
  unrelated triggers would give the marker-discharge its budget back. This is a packaging
  change (how the os module is partitioned for proving), high blast radius.
- **A Why3 trigger/weight tuning** so the marker insert axiom is the FIRST thing tried at the
  marker atom (an emission/prover-config change), reducing the search the full context induces.
- Investigate whether a SMALL subset of the co-emitted dir axioms (e.g. `scan_reflects_present`'s
  `<==>`, or `dir_lookup_frame`) is the specific pollutant and whether it can be narrowed.

## Patch + reproduction
- Self-contained patch (the marker registry + predicate + the de-trust + direct-write
  `_blit_dir_entry` + `_pad_name` ensures + the cross-validated proof sources):
  `getting-better/PROPOSAL-write-dir-entry-detrust-v2.patch` (`git apply` from repo root,
  applies on clean HEAD).
- Cross-validated proof sources are inside the patch
  (`test-suite/corpus/pycsl-reference/0716.proofs/{rocq,lean}/DirBlitMarker.{v,lean}`),
  re-compilable: `coqc DirBlitMarker.v` (Section Variables only); `lean DirBlitMarker.lean`
  (`[propext, Quot.sound]`, no sorry).

## TCB statement
The marker intro/insert, if the integration could be made to discharge the FULL gate, would
ADD a NEW emitted cross-validated axiom that a LIVE os trust would depend on — a human TCB
decision (the user's explicit sign-off), never the loop's to ship autonomously. As it stands
the full body gate reds, so there is nothing to ship: the deliverable is this GAP write-up +
the cross-validated marker (banked, eligible) + the reproducible patch. The tree is reverted
to clean HEAD.

## STOP-AT-PROPOSAL
Per the standing instruction: NOT committed, NOT left in the tree. The parent re-compiles the
proofs, sanity-applies the patch, re-runs the gates + soundness probe, then brings the
proposal (split-module / trigger-tuning follow-on) to the human for the TCB sign-off. Route 1
is "insufficient by itself to close the FULL gate, here is exactly why" — an honest GAP, with
the trigger-poison wall genuinely retired and the residual reduced to a single A.7
aggregate-context wall at the real apply site.
