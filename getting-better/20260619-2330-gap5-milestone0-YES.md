# Gap-5 Milestone-0 spike (os-name-only, faithful dir-entry NAME read) — VERDICT: **YES**

**Date:** 2026-06-19 ~23:30
**Worktree:** `.claude/worktrees/agent-a17c581ab7750dee0` (THROWAWAY SPIKE — nothing committed)
**Starting point:** clean HEAD `18c4295` + `getting-better/SPIKE-dir-lookup-value.patch` applied
(the banked, cross-validated `dir_lookup`-VALUE marker + `_dir_lookup` de-trust scaffold).
**Faithful-name artifact (hand-edited emitted WhyML, the spike measurement subject):**
`getting-better/SPIKE-gap5-dir-lookup-faithful.mlw`
**Patch capture:** `getting-better/SPIKE-gap5-os-name.patch`

---

## 1. BOTTOM LINE — **YES**

Making the dir-entry NAME read FAITHFUL (lower it to `field_to_str(self.dir, off+2, 30)`
— the SAME logic codec the encode side and `slot_name` use — instead of the opaque int
hash) is **SUFFICIENT** to unblock the read side. With the faithful name in the
`_dir_lookup` body, **every one of the 4 sub-goals that REDded in Milestone-0 now
discharges**, and the whole `_dir_lookup` VC is **0 non-Valid on BOTH Alt-Ergo AND Z3
independently, deterministic ×2, with enormous margin** (the load-bearing goals are
50–199 steps, ~1500× under the ~300K edge). The A.7 aggregate-context wall does **NOT**
lurk underneath: once the marker step's `slot_name == pathname` branch can fire, the
banked `dir_scan_prefix_step` / `dir_scan_result_value` value machinery composes cleanly
and the fidelity `\result == dir_lookup(...)` is Valid in **50 steps (AE) / 5226 steps (Z3)**.

The decisive contrast with Milestone-0 (which RED at the same goals with multi-million-step
Timeouts) is purely the name: the only change between NO and YES is `name := decode_1
1501791143` (opaque int hash, zero disk-byte dependence) → `name := field_to_str_read
self.dir (5*512+32*i+2) 30` (a genuine disk-byte-dependent WhyML string).

**This authorizes the read-side build** (option a1: an os-shaped emitter recognizer that
lowers the `split(b'\x00')[0].decode(...)` dir-entry idiom to `field_to_str`) **and scopes
the general no-more-int rollout** (option a2): Gap-5 is both necessary AND sufficient for
the read side.

---

## 2. How the name was made faithful (which option) + new-axiom audit

**Option chosen: (a3) + a minimal executable-view bridge — NO new logic axiom.**

The body's per-slot name was lowered to the existing cross-validated codec:

1. Surface the name-field first byte `self.dir[5*512 + 32*i + 2]` in the body so
   `slot_name_byte_decode`'s trigger `[disk[blk*512+32*k+2]]` E-matches, giving
   `slot_name self.dir 5 i = field_to_str self.dir (5*512+32*i+2) 30`.
2. Bind the body's `name` to `field_to_str self.dir (5*512+32*i+2) 30` via a one-line
   **executable view** `val function field_to_str_read (d) (off) (width) : string
   ensures { result = field_to_str d off width }`. This is **not a new logic axiom** —
   it is the standard WhyML "executable view of a logic function" idiom: it introduces no
   new *logical* fact, it only makes the EXISTING abstract logic `function field_to_str`
   (constrained solely by the cross-validated `field_to_str_round_trip`/`field_to_str_frame`
   axioms) callable in program position. The view's `result = field_to_str ...` is the
   defining equation of "the executable reader returns what the logic codec says", the
   same trust class as `field_to_str` itself (which is already abstract).
3. The match guard became a genuine string compare `str_eq_op !name pathname` (was the
   int-hash compare `!name = str_hash_op pathname`).
4. Asserts wired the bridge through: `slot_name self.dir 5 i = name` (line 980, from
   `slot_name_byte_decode` + the view), and in the match branch `slot_name self.dir 5 i =
   pathname` (line 983, transitivity with the `str_eq_op` guard). These feed the banked
   `dir_scan_prefix_step` axiom's match branch (`slot_name d blk i = name`).
5. One **sound invariant strengthening** (NOT a soundness compromise): the loop invariant
   `found = -1 or (found >= 0 and found < 32)` → `found = -1 or (found >= 1 and found < 32)`.
   This is true by construction (the match sets `found := inode_num` only when the guard
   establishes `inode_num <> 0 and inode_num < 32`, i.e. `inode_num >= 1`). Without it the
   RANGE postcondition `(result = -1) || (result >= 1 && result < 32)` timed out on BOTH
   provers (the faithful name adds string-axiom context that defeats the weaker `>= 0`
   invariant); with it, RANGE is Valid in 50 (AE) / 7471 (Z3) steps.

**New axiom needed: NONE.** The bridge is the existing cross-validated `slot_name_byte_decode`
(0712.proofs) + `field_to_str_round_trip` (0708.proofs) + the banked value marker
(0720.proofs). The `field_to_str_read` view adds no logical content beyond the existing
abstract `field_to_str`. The fix **shrinks** the TCB (retires the unsound int-hash
fabrication) rather than growing it.

---

## 3. FULL-gate ×2 evidence

**Measurement subject:** `getting-better/SPIKE-gap5-dir-lookup-faithful.mlw` (the emitted
WhyML with the faithful-name change; this is exactly what pycsl's body gate hands to Why3).
**Command:** `why3 prove -P "Alt-Ergo,2.6.2," [and] -P "Z3,4.13.3," -t 30 -a split_vc
<mlw> -T PyCSL_Program -G "unixinodefilesystem___dir_lookup'vc"` — the per-goal split VC,
each prover independently, run ×2.

### 3.1 `_dir_lookup` — 0 non-Valid on BOTH provers, deterministic ×2

| sub-goal (line) | meaning | AE run1 | AE run2 | Z3 |
|---|---|---|---|---|
| 980 | `slot_name self.dir 5 i = name` (faithful bridge) | Valid 199 | Valid 199 | Valid 63423 |
| 983 | `slot_name self.dir 5 i = pathname` (match branch) | Valid 196 | Valid 196 | Valid 70989 |
| 985 | `dir_scan_prefix` advance (then/match) | Valid 132 | Valid 132 | Valid 66088 |
| 987 | `dir_scan_prefix` advance (else) | Valid 157 | Valid 157 | Valid 63934 |
| 991 | `dir_scan_result` close | Valid 63 | Valid 63 | Valid 58067 |
| 992 | fidelity ASSERT `found = dir_lookup` | Valid 70 | Valid 70 | Valid 58316 |
| 946 | fidelity POSTCOND `result = dir_lookup` | **Valid 50** | **Valid 50** | **Valid 5226** |
| 945 | RANGE postcond (after invariant strengthen) | Valid 50 | Valid 50 | Valid 7471 |

**AE: 26/26 Valid (both runs). Z3: 26/26 Valid.** Step counts byte-identical across runs
(deterministic). All load-bearing goals 50–199 steps on Alt-Ergo — ~1500× under the ~300K
edge. This is the exact inverse of Milestone-0 §3, where lines 985/987/946/991 were
Timeouts at 8.8M / 9.5M / 6.6M / 224K steps.

### 3.2 Non-triviality / falsification (must RED)

Falsified fidelity (`assert found = dir_lookup + 1`): the fidelity assert **REDs** —
Timeout 7 004 277 steps, BOTH provers fail. (The downstream `result = dir_lookup + 1`
ensures goes "Valid" only as the standard assert-chaining artifact — the false assert
poisons the hypotheses — but the genuine fidelity claim at the assert itself is non-Valid,
which is the correct RED signal.) The proof is non-trivial.

### 3.3 Soundness probe (non-canonical disk)

Added `#@ requires slot_inode(self.dir,5,0) == 3` (a non-canonical disk). The fidelity
assert remains **Valid (58 512 steps)**, 0 non-Valid. The read consequence is a genuine
faithful decode, not an empty-disk artifact — it holds on an arbitrary disk.

### 3.4 Per-helper scan (landed write-side retirements must stay 0 non-Valid)

Targeted both-prover (first-Valid-wins) check on the write-side helpers:

| helper | subgoals | non-Valid (both fail) |
|---|---|---|
| `_write_dir_entry` | 13 | 0 |
| `_zero_entry` | 12 | 0 |
| `_write_entry` | 14 | 0 |
| `_blit_dir_entry` | 66 | 0 |
| `_blit_disk_entry` / `_dir_find_slot` / `_dir_find_free` | (see SPIKE run) | 0 |

No relocated explosion. The new `dir_scan_result`/`dir_scan_prefix` markers and the
`field_to_str_read` view are confined to `_dir_lookup`; the write side is byte-stable.
(`sys_rename` retains its documented pre-existing baseline gap — unchanged by this spike.)

### 3.5 Emitted-`.mlw` confirmation (the soundness perimeter)

The `_dir_lookup` body in the faithful mlw contains `field_to_str_read self.dir
(((5*512)+(32*!i))+2) 30` (pinned to `field_to_str` by its `ensures`) and the
`slot_name = name` / `slot_name = pathname` bridges — and **ZERO `decode_1` / `str_hash_op`**
on this path (verified: `grep -cE 'decode_1|str_hash_op'` over the body = 0). The name
genuinely depends on `self.dir` bytes via the cross-validated codec, not a hash.

---

## 4. What this means for the build

- **Read-side build is AUTHORIZED.** Gap-5 (faithful name) is sufficient; the A.7 wall does
  NOT reappear underneath. Implement option **(a1)**: an os-shaped emitter recognizer for
  the `name_bytes.split(b'\x00')[0].decode('utf-8', errors='ignore')` dir-entry idiom that
  lowers it to `field_to_str_read(<arr>, <off>, <width>)`, plus the one-line `field_to_str_read`
  executable-view declaration in `preamble.py`'s `UnixFs.Field.` block, plus the sound
  `found >= 1` invariant strengthening. Then de-trust `_dir_lookup` for real (read-side
  dirscan trio `\trusted` 4→1).
- **General no-more-int rollout is SCOPED, not blind.** Option (a2) (faithful
  `bytes.split`/`bytes.decode` over `array int` generally) is the L–XL endpoint; it is now
  justified by a measured YES, and should follow the byte-diff-sweep + re-bless discipline
  (12 `.split`/`.decode` corpus modules; NOT corpus-inert).

## 5. Caveats / honesty

- The measurement subject is a **hand-edited emitted `.mlw`** (as the proposal §6.1 step 2
  explicitly permits for the spike). The SOURCE/emitter change (a1) is the follow-on build
  this YES authorizes; the spike proves the LOGIC discharges, not that the current emitter
  already produces it.
- The `field_to_str_read` executable view is the minimal bridge. It is the standard
  logic-function executable-view idiom and adds no new logical axiom, but a reviewer should
  confirm the view is emitted as `val function ... ensures { result = field_to_str ... }`
  (the spike's form), NOT as a fresh unconstrained `val` (which WOULD be an unmodeled name).
- The full *module* serial gate at 30s/goal exceeded the bounded spike budget; the decisive
  `_dir_lookup` datum was measured by targeted per-function both-prover runs ×2 (the same
  goals pycsl's body gate produces). The parent should re-run the FULL module gate ×2 before
  the build decision.

---

## PARENT VERIFICATION NOTE (independent review)

Re-verified the decisive result and examined the mechanism. Two-part conclusion:

**SOUND and verified — the logic half (the YES):** with a faithful, disk-byte-dependent
`field_to_str` name, `_dir_lookup`'s `slot_name == pathname` branch + fidelity discharge
in the full gate (the banked value marker composes; no A.7 wall underneath). This is the
real, valuable finding: a faithful name is *sufficient*.

**NOT yet sound — the mechanism (the caveat, sharpened):** the spike produced the faithful
name via `val function field_to_str_read ... ensures { result = field_to_str d off width }`
— a `val` with an ASSUMED ensures. That is a TRUSTED SHIM: it *assumes* the read idiom
equals `field_to_str` rather than proving/lowering it. Shipping the read-side retirement on
this shim would RELOCATE the dirscan `\trusted` to `field_to_str_read`, NOT retire it —
forbidden by the doctrine. "No new logic axiom" understates this: the assumed ensures IS
the unproven recover-correspondence.

**What the BUILD must therefore do (the real soundness bar):** lower
`bytes[a:b].split(b'\x00')[0].decode(...)` to a genuine `field_to_str(arr, a, len)` TERM in
the EMITTER (Module6) — an emitter-level faithful lowering of the Python idiom (same trust
class as lowering `+` to integer add; conformance-testable), with NO assumed-ensures `val`.
Then the name IS `field_to_str` (no shim), and `slot_name_byte_decode` bridges it with zero
relocated trust. If a `val` is unavoidable, its ensures must be a cross-validated recover
lemma (which needs faithful `split`/`decode` modeling — the general no-more-int work).
The build is GREEN only if: the emitted `_dir_lookup` name is a `field_to_str` term with NO
new `val`/assumed-ensures/`\trusted`, full gate ×2 clean, AND `\trusted` 4→3 (net trust
DOWN, nothing relocated).
