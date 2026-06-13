# RESUME STATE

## DIRECTORY-FRAME REWORK — DIAGNOSIS 2026-06-13 (investigation, no model change yet)
Goal: close the body-gate residual (97 goals) by reworking the directory-frame model.
Built a fast per-writer loop (`why3 prove -T PyCSL_Program -G "unixinodefilesystem___set_bitmap'vc"`
on a kept mlw). Findings (all on `_set_bitmap` = simplest disjoint writer, baseline 6 slow goals):
- **line-436 byte-range invariant is a MINOR cost**: removing it ENTIRELY clears only ~2/6.
- **`block5_decode_frame` axiom multi-pattern trigger** (`[slot_inode d1 5 k, slot_inode d0 5 k
  | slot_name …]`, logic unchanged so Rocq/Lean validation holds) helps marginally (6→4) and
  converts some OOM→Timeout.
- **All triggers combined (byte-range + uniqueness + slot-frame + block5 axiom): plateau at 4.**
- **MORE TIME DOESN'T HELP**: the 4 survivors are "Type invariant" sub-goals that Timeout at BOTH
  30s AND 120s (150–215k steps) — genuinely hard, not slow-but-provable.
- **Removing BOTH disk invariants (byte-range + uniqueness)**: `_set_bitmap` 6→2, `_alloc_block`
  ~10→6. ⇒ the dominant writer cost is the **per-writer MAINTENANCE of the byte-range +
  uniqueness class invariants** (re-deriving the double-forall after each disk write), NOT the
  invariants themselves (which are needed for correctness) and NOT line 436 specifically.
- **THE FIX = frame lemmas applied EXPLICITLY per writer.** A writer proves its cheap local
  byte-frame, then applies `uniq_frame(\old(disk), disk)` / `byte_range_frame(...)` to discharge
  maintenance in O(1) (upper bound = the 6→2 removal result). Needs: (1) named predicates `uniq`,
  `inode_bytes_valid` used in BOTH the class invariant AND the lemma conclusion (so they align);
  (2) the two frame lemmas (provable from `block5_decode_frame` + def — `#@ lemma`, why3-checked,
  no new trust); (3) EXPLICIT lemma application in each writer body (auto-trigger instantiation
  fails — can't pin d0=\old, d1=new). OPEN QUESTION before building: does PyCSL support calling a
  `#@ lemma` function with explicit args (incl `\old(...)`) from a method body? (`#@ proof` is only
  an ordering edge; `let lemma` auto-instantiation hits the same pinning wall.) Validate that first.
  Experiment mlws in /tmp: bg.mlw (baseline), bg_trig3.mlw (all triggers), bg_nodiskinv.mlw (both
  invariants removed = the target state). trig*.py = the transforms.
- **UPDATE-KEYED LEMMA FAILS (the would-be clean fix): mutable-field semantics.** Tried defining
  `predicate uniq` + an update-keyed frame lemma `forall d k v [uniq (d[k<-v])]. (k<2560 \/ 3072<=k)
  -> uniq d -> uniq (d[k<-v])` (trigger pins d,k,v with no \old needed). It did NOT fire — set_bitmap
  stayed at 4 Timeout (not the target 2). Cause: `self.disk` is a MUTABLE record field, so why3's WP
  updates it in place and the exit-invariant goal is NOT a syntactic `(entry_disk)[k<-v]` term, so the
  trigger never matches. (trig4.py).
- **THE REAL WALL = tool development, not a model edit.** The clean frame-lemma fix needs EXPLICIT
  application with the pre-state in each writer body: `uniq_frame(\old(self.disk), self.disk)`. But
  PyCSL lemma application takes VALUE args (0559: `to_int_nonneg(m)`), not the spec-level `\old(...)`.
  So closing the writers requires EITHER (a) extend PyCSL to apply a `#@ lemma` with an `\old`/pre-state
  argument inside a writer body (new frontend+Module5/6 feature), OR (b) restructure the disk writers
  so why3 can frame the mutable field automatically (e.g. write through a functional-update helper that
  exposes `d[k<-v]`, or split the heavy invariants off the type into explicit per-method ensures proven
  in small context). Both are multi-session. CONFIRMED DEAD CHEAP/MEDIUM LEVERS: byte-range rework,
  axiom triggers, invariant triggers, +120s budget, update-keyed lemma — none close the writers.

## ✅ CONSOLIDATED 2026-06-13 (main `aa17948`)
The body-gate effort is consolidated to a clean milestone and gap-1..5 is MERGED to main:
- **Body gate measured (sound):** standalone `pycsl pure_lib/os/UnixInodeFileSystem.py`
  proves **1573/1670 method-body goals (94.2%)** — the FIRST real verification of the
  `sys_*` bodies. Residual 97 (27 OOM, 47 Timeout, 23 Unknown) share ONE root cause: the
  line-436 quantified byte-range class invariant re-established on every disk write. A
  `[disk[i]]` trigger is a partial (~2x) win, not a full fix. KNOWN-HARD, deferred.
- **gap-1..5 typing merged to main** (commit `aa17948`), os `__init__` GREEN. Merging
  needed two faithful model fixes (inlining had hidden both): `sys_chmod #@ no_inline`
  (modular boundary like stat/lstat — correct `array int` typing bloated the inlined
  chmod VC to OOM) + `chmod(filepath: str)` (was defaulting to int).
- **Per-function axiom scoping: tested, NO benefit, reverted** (`b1e1d12`).
- Remaining os work (deferred, deep): chmod/truncate functional namespace frame,
  content_round_trip (gap-17 arc), readlink target value (unmodeled).

Everything below is the pre-consolidation detail (still accurate for the residual).

---

# RESUME STATE — 2026-06-12 (shutdown checkpoint)

Everything is committed to git (nothing lost on shutdown). This file is the single
entry point to restart. Read it + the linked plan docs, then continue.

## Restart process (bring the machine back up)
1. Power on; open a terminal at `/home/fabrice.derepas@canonical.com/git/pycsl`.
2. Sanity-check the toolchain (no rebuild needed — all in place):
   - `.venv/bin/python3.14 --version` (the project venv; pycsl runs as
     `.venv/bin/python3.14 src/pycsl/pycsl.py <file>`).
   - `eval "$(opam env --switch=coq-4.14)"` then `why3 --version`, `coqc --version`
     (8.20.1), `~/.elan/bin/lean --version` (4.30.0) — only needed for proof / axiom
     cross-validation, not for `--no-proof` typecheck.
3. `git status` — should be clean except pre-existing untracked `*.md` plan files and a
   modified `why3-semantics` submodule (both pre-existing, NOT this session's work).
4. `git branch` — three relevant branches (below). Check out the one you'll resume on.
5. Re-read this file, then `body-gate-refactor-plan.md` (on the body-gate branch) and the
   memories (`os-gate-does-not-verify-method-bodies`, `os-coverage-progress`).

## Branches and what's on them

### `main` (green, the consolidated deliverables) — HEAD `bd70104`
The os PUBLIC-API consequence coverage + the str/list-element tool fix. os `__init__`
gate is GREEN (run: `pycsl pure_lib/os/__init__.py` → "Verification SUCCESS", scan for
ANY non-Valid incl. "Out of memory"). Key commits (newest first):
- `bd70104` stat/lstat path-link — functional consequence proves (the str-list payoff)
- `6598ce2` string-element lists — `listdir`/`scandir` return `array string` (corpus BYTE-IDENTICAL)
- `c5a7743` honest test hygiene (dropped logically-false readlink/stat theorems)
- `45410ee` convergence r2 — open_absent closed; symlink/makedirs presence
- `dbd3555` convergence r1 — whole-API coverage (dup, pure helpers)
- `28f5720` REVERT of the gap-17 write-side (it broke the wrapper gate via lookup_frame OOM)
- `5eb32d3` skill docs: dropped obsolete pycsl_copy/ refs
PROVEN through the API (formal_os_*.py, internals-blind): namespace mutators, access,
open (incl. ENOENT), fstat, dup (+shared inode), read, listdir/scandir, makedirs,
symlink presence, stat/lstat (valid inode), pure helpers. `\trusted` = 7.

### `body-gate-array-tuple-typing` — HEAD `5f3f328` (the standalone body-gate work)
Goal: get `pycsl pure_lib/os/UnixInodeFileSystem.py` (STANDALONE) to verify the `sys_*`
METHOD BODIES — a real, sound body gate (the `__init__` gate emits methods as trusted
`val`s and does NOT verify their bodies; see [[os-gate-does-not-verify-method-bodies]]).
- gaps 1-5 (committed, GATED): the TYPECHECK cascade is COMPLETE — `pycsl … --no-proof`
  → `L3-tc ✓`. (gap-1 method-stub `\result[i]`→Array.get; gap-2 per-slot tuple types;
  gap-3 tuple-unpack-target typing; gap-4 list-literal local as array value; gap-5
  scalar quantifier binders shadow same-named locals.) Full inventory:
  `body-gate-refactor-plan.md` on this branch.
- `5f3f328` per-function axiom scoping — NOW TESTED (2026-06-13): **SOUND but ZERO
  proof-perf benefit. DO NOT LAND.** Implemented + gated (all 10 axiom-citing corpus
  files still prove; mechanism fires: 14 per-func `assume`s, 2 class-inv axioms kept
  global). But the standalone-os 3s-triage is IDENTICAL before vs after: **1445 Valid,
  225 Timeout, 1670 goals BOTH ways.** The hypothesis (global axioms poison NON-citing
  method VCs) is WRONG — non-citing methods prove fast either way; the 225 slow goals
  are the CITING methods' inherently-heavy VCs (which keep the axioms as `assume` =
  same content). So scoping is not the fix; revert it before any merge.

### RESULT 2026-06-13 — full body-gate proof FINISHED: 1573/1670 Valid (94.2%)
The detached run completed (`/tmp/bodygate_proof.txt`, exit 2). **1573 Valid, 97 non-Valid**
(27 Out-of-memory, 47 Timeout@30s, 23 Unknown). This is the FIRST sound body-verification
of the 25 `sys_*` METHOD BODIES (the `__init__` gate never did this). Residual analysis:
- 47 Timeout MAY clear with a longer budget; 27 OOM + 22 fast-Unknown (<1s give-up) are
  NOT time-fixable — they need proof engineering.
- Concentrated in the disk MUTATORS: sys_write, _alloc_inode/_block, _set_bitmap,
  _format_disk, unlink, rename, rmdir, _write_directory.
- **SHARED ROOT CAUSE = line-436 class invariant** `\forall i; 512<=i<2560 ==>
  0<=self.disk[i]<=255` (a 2048-byte quantified range). Every disk mutation must
  re-establish this forall; combined with array-update frame reasoning it E-match-OOMs.
  One root cause, not 50. FIX DIRECTIONS (pick when resuming): (a) emit a trigger on the
  invariant quantifier `[self.disk[i]]`; (b) refactor it into a framed logic predicate
  `bytes_valid(disk,512,2560)` so out-of-range writes preserve it trivially and in-range
  writes need only a local lemma; (c) per-mutator `assert` that the update preserves the
  range with a tight trigger.
  TRIGGER TESTED (2026-06-13): hand-adding `[disk[i]]` to the line-40 mlw invariant, on
  _alloc_block: OOM 4->2, many more Valid = PARTIAL win (~2x fewer OOM) but NOT complete
  (residual 2 OOM + 4 Timeout + 4 Unknown). Helps all mutators but residual still needs
  per-fn engineering (trigger + framed predicate + per-mutator frame asserts). To LAND it:
  emitter must put `[disk[i]]` on the class-inv `\forall` lowering.
  FAST ITERATION LOOP (~1min/fn): emit mlw once
  (`pycsl … --keep-mlw --no-proof`), then
  `why3 prove -a split_vc -P "Alt-Ergo,2.6.2," -P "Z3,4.13.3," --timelimit 60 /tmp/bodygate.mlw -T PyCSL_Program -G "unixinodefilesystem___alloc_block'vc"`.

### IN PROGRESS 2026-06-13 — the full body-gate proof IS NOW RUNNING (detached)
WIP scoping reverted (`b1e1d12`); tool back to clean gap-5. The full standalone proof
was LAUNCHED detached: `why3 prove -a split_vc -P Alt-Ergo,2.6.2, -P Z3,4.13.3,
--timelimit 30 /tmp/bodygate.mlw` (mlw emitted from `UnixInodeFileSystem.py` via
`--keep-mlw --no-proof`), `timeout 21600` (6h), output → `/tmp/bodygate_proof.txt`
(finishes with a `PROOF_DONE exit=N` line). Early sample (~4min): 562 Valid + first hard
goals = OOM/Timeout on `_alloc_block'vc`, `_alloc_inode'vc`, `_unpack_direntry'vc`.
TO RESUME: `grep -ic valid /tmp/bodygate_proof.txt`; scan EVERY non-Valid
(`grep -iE 'Prover result' /tmp/bodygate_proof.txt | grep -viE ': Valid'`). The
remaining OOM/Timeout goals (constructor class-inv 136, sys_write, alloc, unlink/rename)
are the targeted follow-on. If the machine was shut down mid-run, re-launch the same cmd.

### KEY 2026-06-13 finding — the body gate is NOT stuck, it's just BIG
The standalone proof has **1670 goals**; ~225 (13.5%) are slow at a 3s timelimit. The
slow goals are dominated by the **constructor class-invariant establishment (136 goals,
`unixinodefilesystem'vc`)** + disk-mutating syscalls (sys_write 27, _alloc_inode/_block
20, unlink/rename/rmdir). Most are SLOW-but-PROVABLE: the constructor class invariant
DOES prove in `__init__` (at 30s). So the 30-min full-proof timeout was simply too short
— at 30s/goal × (Alt-Ergo + Z3) it's ~5–6 HOURS. **To get the sound body gate: run
`pycsl pure_lib/os/UnixInodeFileSystem.py` with a multi-HOUR budget** (background,
poll over hours); it should land mostly-Valid with a handful of genuinely-hard goals to
then target. The per-function axiom scoping detour does not change this. (Run with the
clean gap-5 tool — revert `5f3f328` first.)

### `str-list-elements` — already MERGED to main (ff). The branch can be deleted.

## The two open problems (both = the same deep proof-performance wall)
1. **Standalone body-gate PROOF is impractically slow** (>30-min timeout). Typecheck is
   done (gaps 1-5); the proof times out because the global `UnixFs.Dir.*` axioms
   E-match-blow-up in EVERY method-body VC. The WIP commit `5f3f328` attempts the fix
   (per-function axiom scoping). RESUME = finish + gate it (see its commit message).
2. **chmod/truncate namespace frame** (their functional consequence, on main). Needs
   `lookup_frame` to export `\forall q; dir_lookup` unchanged — but adding it (even WITH
   the multi-pattern trigger `[dir_lookup d1 5 name, dir_lookup d0 5 name]`) OOMs chmod's
   block-5 byte-frame assert (chmod's body `dir_lookup disk 5 pathname` + `\old` partner
   fires the trigger; the `forall k` antecedent explodes). Triggers DON'T fix it.
   Per-function scoping does NOT help here either (chmod is INLINED into its wrapper, so
   the axiom and the poisoned assert share one VC). Likely needs the body gate
   (no_inline chmod with its body verified standalone). `lookup_frame` + the
   cross-validated `LookupFrame.{v,lean}` proofs live in reverted commit `6ed1cf4`
   (recover with `git show 6ed1cf4:<path>`).
Also still open: content_round_trip (write→read, the gap-17 arc — also on the body gate);
readlink target value (genuinely out of scope — symlink target bytes unmodeled).

## How to RESUME the WIP (per-function axiom scoping) — the recommended next step
On `body-gate-array-tuple-typing`:
1. Inspect `5f3f328`'s `_func_has_scopable_body` + the `assume`-injection threading.
2. GATE it (it's behavior-changing → byte-diff WILL differ; gate on PROOFS):
   - Full corpus proof: `bash bin/run-reference-tests.sh` — the axiom-citing corpus
     files (0342 GCD, Perm, Json) must still PROVE (catches a function that implicitly
     relied on a global axiom it doesn't cite).
   - os `__init__` GREEN (0 non-Valid incl. "Out of memory").
   - PAYOFF triage on the standalone: emit mlw (`--keep-mlw --no-proof` on
     `pure_lib/os/UnixInodeFileSystem.py`), then
     `eval "$(opam env --switch=coq-4.14)"; why3 prove -a split_vc -P "Alt-Ergo,2.6.2," --timelimit 3 <mlw> | grep 'Prover result' | sed -E 's/.*is: ([A-Za-z ]+).*/\1/' | sort | uniq -c`
     BEFORE (revert the WIP src files to the branch's gap-5 HEAD) vs AFTER. SUCCESS =
     materially fewer Timeout/OOM, more Valid. If no improvement → scoping isn't the
     bottleneck; report and reconsider.
3. If it gates green AND improves the standalone, push the standalone toward 0-unproven
   (it may reveal more genuinely-slow VCs); then re-establish the os body baseline and
   re-do gap-17 write-side under the now-sound body gate.

## Gating discipline (NON-NEGOTIABLE — caught multiple over-claims this session)
- Re-run the FULL pipeline yourself; never trust a subagent self-report.
- Scan EVERY non-Valid verdict including **"Out of memory"** (NOT matched by
  `Unknown|Timeout|FAILED`). Use `grep 'Prover result' | grep -v ': Valid'`.
- `--fun <method>` is VACUOUS for os method bodies (proves false postconditions) — never
  use it to judge soundness; use the FULL-file run.
- Corpus byte-diff via `bin/byte-diff-sweep.sh` both-ways vs HEAD; NO `git stash`
  (untracked-work hazard). Behavior-changing axiom moves → gate on the corpus PROOF.
- `fabrice:` commit prefix for changes Fabrice made himself (no Claude trailer);
  my own changes keep the trailer.
