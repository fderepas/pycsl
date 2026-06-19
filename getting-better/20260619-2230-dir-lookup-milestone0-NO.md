# Milestone-0 spike — `_dir_lookup` read-side VALUE marker — VERDICT: **NO**

**Date:** 2026-06-19 22:30
**Worktree:** `.claude/worktrees/agent-a43c5b99dba4d9a69` (THROWAWAY SPIKE — nothing committed)
**Patch:** `getting-better/SPIKE-dir-lookup-value.patch` (apply to clean HEAD `14ffc29`)
**Kernel proofs (cross-validated, banked in the patch):**
`test-suite/corpus/pycsl-reference/0720.proofs/{rocq/UnixDirScanValue.v, lean/UnixDirScanValue.lean}`

---

## 1. BOTTOM LINE — **NO**

A cross-validated `dir_lookup`-VALUE marker axiom does **NOT** let the de-trusted
`_dir_lookup`'s fidelity ensures discharge in the FULL body gate. The A.7
aggregate-context wall is **NOT** surmountable for the read side, because the genuine
obstruction is one layer *below* A.7: the **Gap-5 RECOVER** is unmodeled — and in PyCSL
today it is not even type-compatible. The L/XL read-side build is **NOT justified**.

The verdict splits cleanly into what worked and what walled:

- **The value axiom IS cross-validatable (gate 1 PASSED).** The new value theorem +
  loop-carry prefix marker cross-validate zero-TCB in BOTH provers (§2). This part of
  the proposal's premise is sound.
- **The marker CANNOT be established from the body (gate 3 FAILED).** The marker INTRO
  (the prefix-step) requires `slot_name(self.dir, 5, i) == pathname` as its branch
  condition, but the body's per-slot `name` lowers to the **opaque int hash
  `decode_1 1501791143`** with zero dependence on `self.dir` bytes. There is no modeled
  byte→str RECOVER bridge from the disk bytes to that name — and the recover assert
  `slot_name(...) == name` is not even type-compatible (`slot_name : string` vs the
  body's `name : int` hash). So the marker step's branch can never be selected, the
  prefix invariant cannot advance, and the chain explodes (multi-million-step Timeouts).
- **FULL gate ×2, deterministic, NO margin (§3).** `_dir_lookup` has **4 non-Valid in
  BOTH runs** (2 in-loop Assertions ~8.8M / ~9.5M steps, the fidelity Postcondition
  ~6.6M steps, the marker-close Assertion ~224–228K steps). Not near-misses — A.7
  explosions. The de-trust REDS the gate (baseline: 3 non-Valid, all `sys_rename`; spike:
  +4 on `_dir_lookup`). Step counts byte-stable across runs (8 822 532 in both).
- **Landed write-side retirements intact (§4).** `_write_dir_entry` / `_zero_entry` /
  `_write_entry` (+ `_dir_find_slot/_free`, `_blit_*`) all 0 non-Valid in the spike run —
  the new `dir_scan_result` marker is a distinct unique atom and does not poison them.
  No relocated explosion; the new explosion is confined to `_dir_lookup` itself.

A clean NO. It saves the L/XL build: the read side needs a **byte→str RECOVER name model
(Gap-5)** before any value axiom can be *applied*. The value axiom alone — the piece the
proposal said was the missing dual — is necessary but **far from sufficient**.

---

## 2. The value theorem + marker + cross-validation (gate 1 PASSED)

Authored in the existing `UnixDirScan.v` kernel section (same abstract `slot_inode`/
`slot_name`/`scan` as `scan_reflects_present`, so provably consistent — both are theorems
over the one `scan` Fixpoint):

- `dir_scan_result d blk name r` ≜ `scan d blk name 16 (-1) = r` (the marker, definitional).
- **`dir_scan_result_value`**: `dir_scan_result d blk name r -> dir_lookup d blk name = r`
  (the load-bearing read dual of `dir_blit_marker_value_inode`; the inductive
  last-live-match witness is discharged offline — `dir_lookup := scan ... 16 (-1)`).
- **prefix loop-carry rungs** (the NON-inductive rung the WhyML loop needs):
  `dir_scan_prefix_base` (init = -1), `dir_scan_prefix_step` (one slot, O(1), the body's
  `if` update), `dir_scan_prefix_close` (i=16 ⇒ `dir_lookup = r`).

**Cross-validation outputs:**

Rocq (`Print Assumptions`, all theorems):
```
dir_scan_result_value      : Closed under the global context
dir_scan_result_intro      : Closed under the global context
dir_scan_prefix_base       : Closed under the global context
dir_scan_prefix_step       : Closed under the global context
dir_scan_prefix_close      : Closed under the global context
```

Lean (`#print axioms`):
```
dir_scan_result_value  : does not depend on any axioms
dir_scan_result_intro  : does not depend on any axioms
dir_scan_prefix_base   : does not depend on any axioms
dir_scan_prefix_step   : depends on axioms: [propext, Quot.sound]   (allowed)
dir_scan_prefix_close  : does not depend on any axioms
```

Registered in `preamble.py` as `UnixFs.Dir.dir_scan_prefix_base/_step`,
`dir_scan_result_intro/_value`, each marker-keyed (`[dir_scan_prefix d blk name i r]` /
`[dir_scan_result d blk name r]`) — once-firing, never on a bare `dir_lookup`/`slot_inode`
term. The two predicates `dir_scan_result`/`dir_scan_prefix` are declared in
`_AXIOM_FUNCTIONS["UnixFs.Dir."]`.

---

## 3. FULL-gate ×2 evidence (the decisive datum)

Command: `PYTHONHASHSEED=0 pycsl pure_lib/os/UnixInodeFileSystem.py --no-typecheck`,
run ×2, Alt-Ergo + Z3, 30s/goal.

**Baseline (HEAD, 4 trusts intact):** 3 non-Valid — all `sys_rename` (1 Assertion OOM
17.83s + 1 Assertion Timeout 252 487 steps; the documented pre-existing GAP). Everything
else, including the 3 trusted read helpers, Valid.

**Spike (`_dir_lookup` de-trusted, marker cited):** `_dir_lookup` sub-goals —

| sub-goal | run 1 | run 2 |
|---|---|---|
| Assert: `slot_inode = 256*b0+b1` (byte-decode) | **Valid 5448** | **Valid 5448** |
| Loop invariant init (`dir_scan_prefix` base) | **Valid** | **Valid** |
| Postcondition: RANGE | **Valid 5222** | **Valid** |
| Assert: `dir_scan_prefix` advance #1 | **Timeout 8 822 532** | **Timeout 8 822 532** |
| Assert: `dir_scan_prefix` advance #2 | **Timeout 9 492 112** | **Timeout 9 559 146** |
| Postcondition: **FIDELITY** `= dir_lookup` | **Timeout 6 592 662** | **Timeout 6 591 603** |
| Assert: `dir_scan_result` close | **Timeout 228 328** | **Timeout 223 590** |

**4 non-Valid on `_dir_lookup` in BOTH runs**, deterministic, multi-million steps (no
margin under the ~300K edge — they are 20–30× over it). The de-trust REDS the gate. The
byte-decode bridge fires (the `slot_inode` assert + RANGE are Valid), and the marker BASE
init is Valid — but the marker STEP/advance cannot fire (it needs the unmodeled
`slot_name == pathname` branch), so `dir_scan_result` is never established and the value
axiom never applies.

Identical diagnosis in `--fun` isolation (already 4 Timeouts there) — this is NOT merely
the full-module apparatus; the logic gap (Gap-5) is present even in isolation.

**Falsification / soundness probes:** moot. The fidelity ensures never PROVES (it is a
Timeout, not Valid), so there is no false green to falsify and no empty-disk artifact to
soundness-probe — exactly the situation the prior GAP doc §6 recorded. (A read helper does
not mutate, so the `\old==self` vacuity collapse does not apply either.)

---

## 4. Per-helper scan (no relocated explosion; write side intact)

In the spike full-gate run, non-Valid counts:
```
_write_dir_entry : 0   _zero_entry : 0   _write_entry : 0
_dir_find_slot   : 0   _dir_find_free : 0
_blit_dir_entry  : 0   _blit_disk_entry : 0
```
Only `_dir_lookup` gained non-Valid goals; the 3 landed write-side retirements and all
sibling byte mutators stay clean. The `dir_scan_result` marker (distinct unique atom)
does not fire inside any write helper.

---

## 5. The precise wall (why read ≠ write, restated with the emitted .mlw)

The emitted `_dir_lookup` body (`--keep-mlw`) makes the obstruction syntactic:
```
b0 := self.dir[((5 * 512) + (32 * !i))];          (* literal offset — slot_inode bridge FIRES *)
assert { (slot_inode self.dir 5 !i) = ((256*!b0)+!b1) };   (* Valid *)
name := (decode_1 1501791143);                    (* OPAQUE INT HASH — zero disk-byte dependence *)
... guard: !name = str_hash_op pathname ...        (* int-hash compare, NOT slot_name *)
assert { dir_scan_prefix self.dir 5 pathname (!i+1) ... }  (* Timeout — step branch undecidable *)
```
- **inode half: solved.** The literal-offset byte surface + `slot_inode_byte_decode`
  bridges `slot_inode self.dir 5 i = 256*b0+b1` (Valid). The write-side lever transfers.
- **name half: WALLED (Gap-5 RECOVER).** The body's `name` is `decode_1 <hash> : int`.
  The marker step needs `slot_name self.dir 5 i = pathname` (string). `slot_name_byte_decode`
  only gives `slot_name = field_to_str(off+2,30)`; there is no axiom equating
  `field_to_str(...)` to the body's `decode_1` hash, and the two are not even the same
  WhyML type. So the step's guard is undecidable ⇒ the marker never advances ⇒ the value
  axiom (correct & cross-validated) has nothing to apply to.

This is the read-side-specific obstruction the design proposal flagged as the dominant
secondary risk (§3.3 lever / §2.2 Gap-5) and the prior GAP doc called fatal. The spike
confirms it empirically AND shows the value axiom — the proposal's headline "missing dual"
— is the *easy* half; the RECOVER codec is the real blocker.

---

## 6. What WOULD be required (human-gated, NOT a loop move)

To make the read side retire, in order:
1. **Model the byte→str RECOVER codec (Gap-5).** Give the body's per-slot name a value
   that depends on `self.dir` bytes (not an opaque int hash), then a cross-validated
   `field_to_str`-recover lemma `field_to_str d off 30 = <body name>` so
   `slot_name self.dir 5 i == pathname` becomes derivable when the bytes match. This is a
   substantial model extension (the str/int "no-more-int" leak: the decoded name must be a
   real WhyML `string`, not `decode_1 : int`).
2. THEN the value marker of this spike (already cross-validated) plugs in directly.

Until (1) lands, the read-side `dirscan-fidelity` trio stays a LOGGED GAP. The value-axiom
half is done and banked (`0720.proofs`) for reuse when (1) is built.

**Blast-radius note (minor, fixable):** the 2 new predicate decls were placed in the
general `UnixFs.Dir.` `_AXIOM_FUNCTIONS` list, so they leak into corpus modules citing any
`UnixFs.Dir.*` axiom (byte-diff +2 lines on 0712) — exactly as `dir_blit_marker` already
does (pre-existing accepted behavior). To restore strict byte-identity, gate them under a
`UnixFs.Dir.dir_scan` sub-prefix like `dir_blit_marker_at` is. Not relevant to the verdict.

---

## 7. Hygiene

- Kernel proofs re-verified from the proofs tree: Rocq `coqc` rc=0; Lean rc=0 with the
  axiom set above. No `sorry`/`Admitted`/extra axioms.
- FULL gate measured ×2, PYTHONHASHSEED=0, Alt-Ergo+Z3, deterministic.
- Patch captured: `getting-better/SPIKE-dir-lookup-value.patch` (412 lines, 4 files:
  `_dir_lookup` body, preamble axioms+decls, the two kernel proofs). NOTHING committed.
- Tree to be reverted to clean HEAD `14ffc29` keeping only the patch + this writeup;
  stash empty; coq/lean/`.mlw`/`/tmp` artifacts cleaned.
