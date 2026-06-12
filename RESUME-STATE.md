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
