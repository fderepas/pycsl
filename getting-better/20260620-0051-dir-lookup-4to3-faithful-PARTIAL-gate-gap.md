# `_dir_lookup` 4→3 via a SOUND faithful read-name EMITTER lowering — VERDICT: **SOUND LOWERING BUILT & PROVEN per-function; BLOCKED on a GATE-level Z3 combined-pass OOM that regresses the 3 landed write-side retirements**

**Date:** 2026-06-20 ~00:51
**Worktree:** `.claude/worktrees/agent-aa6d64db8b41d7f75` (STOP-AT-PROPOSAL — nothing committed; tree reverted)
**Patch:** `getting-better/PROPOSAL-dir-lookup-faithful-name-detrust.patch` (35 864 bytes, 5 files)
**Starting point:** clean HEAD `4a2494c` (Gap-5 Milestone-0 YES banked).

---

## 1. BOTTOM LINE

The **sound emitter lowering is BUILT and the read side discharges** exactly as the spike
predicted — with a GENUINE `field_to_str` TERM, **NO shim, NO `val…ensures` bridge, NO new
`\trusted`, NO new axiom**, and a **corpus-narrow** recognizer. Per-function, `_dir_lookup`
is **0 non-Valid on best-of-both-provers, deterministic ×2, with margin** (Z3 24/24 Valid
both runs, max 70 878 steps ≪ ~300K; AE 23/24, the one residual covered by Z3); the
fidelity falsification (`+1`) is RED on both provers (non-trivial); the source `\trusted`
count is **4→3** (the dirscan-fidelity directive on `_dir_lookup` removed, nothing added).

**BUT the retirement CANNOT be landed as-is:** adding the read-side `field_to_str`
machinery to the SAME module as the write side makes the pycsl **body GATE's full-file Z3
first-pass run OUT OF MEMORY**, which truncates Z3's per-goal results and causes the gate to
mis-report two of the three LANDED write-side retirements (`_write_dir_entry` → OOM,
`_zero_entry` → "1 unproven") as FAILED — even though each of those functions is **0
non-Valid on best-of-both-provers when proved in isolation** (verified: `_zero_entry` Z3
12/12 AND AE 12/12; `_write_dir_entry` covered AE@1142 + Z3@1144). The regression is a
**prover-memory / gate-orchestration interaction**, not a genuine proof failure — but it
violates the mission's hard bar ("the 3 landed write-side retirements STILL 0 non-Valid"
through the gate). **This is the precise GAP.** I did NOT fall back to the shim.

---

## 2. The recognizer (file:line) + faithfulness argument + emitted-`.mlw` proof

### 2.1 The recognizer — `src/pycsl/module6_whyml/expressions.py`
- `_recognize_field_decode_idiom` (the narrow matcher), wired into `_handle_call_expr`
  immediately after arg-lowering, gated `if func_name == "decode"`.
- Helpers: `_is_null_byte_lit` (matches `b'\x00'` = `ArrayLit[Number 0]`), `_linear_form`
  / `_static_width` (affine fold of `upper - lower` so the field WIDTH `30` is a literal
  even though both bounds carry the loop variable `i`).

It matches EXACTLY `<arr>[<a>:<b>].split(b'\x00')[0].decode('utf-8', errors='ignore')` and
lowers it to the TERM `(field_to_str <arr> <a> <b-a>)`. It DECLINES (returns None, leaving
the existing opaque path byte-identical) unless ALL hold: decode 1st arg is `'utf-8'`;
receiver is `Subscript[0]`; over a `split` call whose sole arg is the byte literal
`b'\x00'`; whose receiver is a genuine `SliceAccess` (`arr[a:b]`, no step); with a
statically-known width.

### 2.2 Faithfulness (the emitter's responsibility, conformance-tested)
`bytes[a:b].split(b'\x00')[0].decode('utf-8', errors='ignore')` = the bytes from `a` up to
the first null within the `b-a`-byte window, read as a UTF-8 string = `field_to_str(arr, a,
b-a)` by `field_to_str`'s scan-to-first-null definition (0708.proofs). For the dir-name
field (`>H30s`: 2-byte inode + 30-byte null-padded name), the source slices
`self.dir[5*512+32*i+2 : 5*512+32*i+32]` (width 30), so the term is `field_to_str self.dir
(5*512+32*i+2) 30` = `slot_name self.dir 5 i` by the cross-validated `slot_name_byte_decode`
(0712.proofs). Same trust class as lowering `+` to integer add.

### 2.3 No-relocated-trust grep over the emitted os `.mlw` (PASS)
```
field_to_str_read shims ................ 0
new val…ensures referencing field_to_str  0
field_to_str decl ...... val function field_to_str (d: array int)(off:int)(width:int):string   (NO ensures)
decode_1 / str_hash_op in _dir_lookup body  0
_dir_lookup name term .. let name = ref (field_to_str self.dir (((5*512)+(32*!i))+2) 30) in
\trusted reviewer directives (source) ... HEAD 4 → worktree 3   (dirscan-fidelity on _dir_lookup removed; nothing added)
```
`field_to_str` is promoted to `val function` (program-callable) — the SAME abstract symbol
the axioms constrain, the identical idiom already used for `bit_and`/`struct_pack_i1a1`/
`json_mirror`. `val function` adds NO logical content (no ensures, no new symbol, no new
axiom). It is NOT the spike's `field_to_str_read … ensures { result = field_to_str … }`
shim (which is absent: grep = 0).

---

## 3. Value-proof cross-validation (0720.proofs — banked, recompiled)

`test-suite/corpus/pycsl-reference/0720.proofs/{rocq,lean}/UnixDirScanValue.{v,lean}`
(the dir_scan_result / dir_scan_prefix VALUE marker family; the field_to_str_read shim was
DROPPED — unnecessary now that the name is a real `field_to_str` term):
- **Rocq** (`coqc`, full init): compiles 0 errors; every theorem `Print Assumptions` =
  **"Section Variables:" only** (0 global Axiom, 0 Admitted) — dir_scan_result_value,
  dir_scan_result_intro, dir_scan_prefix_base/step/close.
- **Lean** (`lean`): 4 theorems "does not depend on any axioms"; `dir_scan_prefix_step`
  ⊆ `{propext, Quot.sound}`. No sorry.

The marker fires ONLY at the atoms `_dir_lookup` asserts (loop-carry invariant + loop-exit
close), keyed `[dir_scan_prefix …]` / `[dir_scan_result …]` — never on a bare
dir_lookup/slot_inode term. The inductive last-live-match argument is discharged OFFLINE in
the kernel; SMT applies one O(1) step per rung.

---

## 4. Per-function VC evidence (the read side discharges; the write side is clean in isolation)

### 4.1 `_dir_lookup` — 0 non-Valid, best-of-both, deterministic ×2, with margin
Standalone `why3 prove -a split_vc -G unixinodefilesystem___dir_lookup'vc`:

| run | Z3 | AE | union |
|---|---|---|---|
| 1 | **24/24 Valid** (max 70 878 steps) | 23/24 (only line 959 `slot_name=name` Timeout) | **0 non-Valid** |
| 2 | **24/24 Valid** (byte-identical) | 23/24 (same) | **0 non-Valid** |

The pycsl body gate `--fun unixinodefilesystem___dir_lookup` → **SUCCESS! All contracts
formally proven** (×2). Margin: load-bearing goals 50–199 steps (AE) / ≤70 878 (Z3), ≫
1500× under the ~300K edge.

### 4.2 Genuineness / falsification (must RED) — PASS
Perturbing the loop-exit fidelity assert `!found = dir_lookup …` → `… + 1`: **Timeout on
BOTH provers** (Z3 7.17 M steps, AE 167 930 steps). The real fidelity is Valid; the +1 is
RED. The proof is non-trivial.

### 4.3 The 3 landed write-side retirements — CLEAN IN ISOLATION, but the GATE regresses
| helper | standalone Z3 | standalone AE | union (per-function) | pycsl body GATE |
|---|---|---|---|---|
| `_write_entry`  | — | — | 0 non-Valid | **SUCCESS** |
| `_zero_entry`   | **12/12** | **12/12** | 0 non-Valid | **FAIL: "1 unproven"** ⚠ |
| `_write_dir_entry` | 12/13 (1142 Timeout) | 12/13 (1144 Timeout) | 0 non-Valid (AE@1142 132 steps + Z3@1144 63 246 steps) | **FAIL: Out of memory 16 s** ⚠ |
| `_unpack_direntry` | OOM/Timeout on 2 goals | all Valid | 0 non-Valid | SUCCESS |

The ⚠ rows are the GAP: the per-function VCs are 0 non-Valid, but the gate FAILS them.

---

## 5. THE GAP (precise) — Z3 combined-pass OOM from co-resident read+write field_to_str machinery

**Root cause:** citing `slot_name_byte_decode` + `field_to_str_round_trip` on `_dir_lookup`
EMITS the `field_to_str` family MODULE-WIDE (the documented risk in
`UnixInodeFileSystem.py:1120` — "citing them would EMIT them module-wide … E-match-explode
the sibling"). On HEAD these axioms are NOT in the os module at all (the old trusted
`_dir_lookup` cites nothing), so `field_to_str` has 0 references on HEAD; the write side
proves at ≤474 K steps. With the read-side build:
1. **Direct E-match explosion (FIXED, soundly):** without a trigger, `field_to_str_round_trip`
   auto-selects `[off+i]`/`[off+String.length name]` triggers that E-match the WRITE-side
   per-char / null-pad goals (`dir[2560+32*slot+2+i] = …`) → OOM. **Fix landed:** an
   explicit trigger `[field_to_str d off width]` confines the axiom to read-side goals
   (where a `field_to_str` term exists). Sound (a trigger only RESTRICTS instantiation);
   the 4 changed corpus byte-codec tests (0708/0711/0712/0714) still verify SUCCESS.
2. **Residual combined-query memory pressure (NOT FIXED):** even with the trigger, the pycsl
   gate's first pass runs Z3 on the WHOLE FILE at once (`why3 prove -a split_vc` over every
   function's VC). The added `val function field_to_str` + the `_dir_lookup` body's
   `field_to_str` round-trip goal push Z3's combined-pass memory over the edge → **Out of
   memory ~16–22 s**, the Z3 process dies, partial output truncates per-goal verdicts, and
   the per-goal Alt-Ergo residual-fallback never runs on the affected write-side goals → the
   gate mis-reports `_zero_entry`/`_write_dir_entry` as unproven. (`_dir_lookup`,
   `_write_entry`, `_unpack_direntry` happen to survive; `_zero_entry`/`_write_dir_entry`
   don't — borderline.)

**Why this is the GAP and not a shim-able problem:** the lowering itself is sound and the
read side proves; the blocker is that the READ and WRITE `field_to_str`/`slot_name` axiom
families cannot be co-resident in ONE module under the gate's combined Z3 pass without OOM.

### Likely resolution (NOT attempted here — flagged risky, needs the modular boundary)
Put the read side behind a MODULE/opacity boundary so the `field_to_str` round-trip context
is NOT in scope for the write-side VCs — the `#@ no_inline` / `#@ interface`+`#@ reveal`
modular-boundary technique already used for `_pack_inode` (memory: track_b_opacity,
os_coverage_progress). I.e. prove `_dir_lookup`'s fidelity in a context where the
write-side mutators are opaque (and vice-versa), so the two axiom families never share a
single Z3 query. This is an L-sized structural change (module split / opacity wiring), not a
one-line fix, and the user flagged module-splits/reorders as RISKY (feedback_safe_vs_risky_bricks)
→ I stopped at the proposal rather than auto-dispatching it.

Alternatively: tune the gate to run Alt-Ergo FIRST on this module (AE does not OOM here —
it proves every write-side goal and all but line 959 of `_dir_lookup`), but that is a gate
policy change, not a soundness change, and would not by itself prove `_dir_lookup` line 959
(which only Z3 discharges) — so a per-goal split (the gate already does this for residuals,
but the OOM crash pre-empts it) plus per-FUNCTION isolation (one `why3 prove` per function
instead of one for the whole file) is the cleaner gate fix.

---

## 6. Corpus byte-diff scope (recognizer is narrow — PASS)

Full parallel emission sweep, worktree vs clean HEAD (604/605 files): **exactly 4 reference
`.mlw` differ — 0708, 0711, 0712, 0714** (all the `field_to_str`/`slot_name` byte-codec
proof corpus). Each diff is ONLY the 3 intended sound changes: `function`→`val function
field_to_str`; the confining trigger `[field_to_str d off width]`; the 2 new marker
predicate decls. **ZERO mis-lowerings.** `0425.py` (the ONLY other corpus file using the
null-byte split+decode idiom) is **byte-IDENTICAL** — its `name_bytes.split(…)` form has a
VAR receiver, not a `SliceAccess`, so the recognizer correctly DECLINES. No `.expected.mlw`
conformance fixtures exist for the 4 differing files (no re-bless needed). 0001/0425 verify
SUCCESS; doc-coherency `--check` green (no new directive).

---

## 7. Human-sign-off note

This proposal is **NOT ready to land**: the read-side lowering is sound, no-shim, corpus-
narrow, and `_dir_lookup` retires 4→3 per-function with margin, but the body GATE regresses
two of the three landed write-side retirements via a Z3 combined-pass OOM. **Do not commit
until the modular-boundary (or per-function-gate) fix in §5 lands and the FULL body gate ×2
shows all four functions 0 non-Valid through the gate.** The parent should: (a) re-run the
no-relocated-trust grep (`field_to_str_read`=0, no new `val…ensures`/`\trusted`,
`\trusted` 4→3); (b) recompile 0720.proofs (Section-Vars-only / ⊆{propext,Quot.sound});
(c) re-run the corpus byte-diff (only 0708/0711/0712/0714, the 3 intended changes); (d)
decide the §5 boundary approach before bringing the retirement to the human.

**Patch:** `getting-better/PROPOSAL-dir-lookup-faithful-name-detrust.patch`
**Tree:** reverted clean (only patch + this writeup remain).

---

## PARENT VERIFICATION NOTE (independent re-verification)

**Soundness of the mechanism — CONFIRMED clean.** Re-grepped the emitted os `.mlw`:
`field_to_str_read` shim = 0; new `val…ensures field_to_str` = 0; `field_to_str` is a
`val function` with NO ensures (no logical content, like `bit_and`); `_dir_lookup` name is
a genuine `field_to_str self.dir (…+2) 30` TERM (0 `decode_1`); `\trusted` source 4→3,
nothing relocated. This is a GENUINELY SOUND, trust-free retirement mechanism — NOT a shim.

**The blocker — CONFIRMED and SHARPENED (it is NOT merely gate orchestration).** Re-ran:
- Full body gate: produced NO summary output — the Z3 full-file pass exhausts memory and
  the run dies (catastrophic OOM, not a clean mis-report).
- `_zero_entry` (a LANDED, robust retirement) **Times Out at 9,887,117 steps in `--fun`
  isolation** once the read-side `field_to_str` machinery is present in the module preamble.
  Since `--fun` still emits the whole preamble, the added READ-side `field_to_str` axiom
  family is in scope when proving WRITE-side goals and tips them over — an aggregate-context
  (A.7) explosion from read+write `field_to_str` CO-RESIDENCE, perturbing each goal, not
  just a full-file memory artifact. An orchestration tweak (per-goal / Alt-Ergo-primary)
  alone will therefore NOT fix it.

**Conclusion / the real unblock.** The read-side retirement is sound + per-function-proven
+ trust-free, but landing it regresses the write-side via read+write `field_to_str`
co-residence. The fix is exactly the **scope/module-emission feature**
(`scope-emission-design-proposal.md`, PR #38) — verify each function against a SMALLER
axiom set so the read axioms are out of scope for write-side goals (and vice versa). That
feature was MOOT for write-only (the marker recipe beat A.7 within each helper) but is the
GENUINE prerequisite for read+write co-residence. Campaign paused at `\trusted`=4 (entire
write side retired); the sound read-side build is banked in
`getting-better/PROPOSAL-dir-lookup-faithful-name-detrust.patch` for when scope-emission
lands. NOT merged (regresses the write side through the gate).
