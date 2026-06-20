# sys_open fd-resolution-fidelity RETIRED — os bare `\trusted` 1 → 0 (PROPOSAL)

**Result: SUCCESS (proposed).** `sys_open`'s `#@ \trusted reviewer: fd-resolution-fidelity`
— the SOLE remaining bare `\trusted` in `pure_lib/os/` — is retired to the SOUND
free-slot-conditioned form, mirroring the LANDED `sys_dup` retirement (SKILL.md A.14).
With this, **os bare `\trusted` = 0** (strmod already 0): os is fully de-trusted modulo
the cited cross-validated axiom families already in the TCB.

STOP-AT-PROPOSAL: not committed. Patch + this writeup only; tree reverted clean.
Parent re-verifies on a branch in the main checkout.

## 1. The over-claim (why the trust existed) and the conditioned-form diagnosis

The trust covered two UNCONDITIONED bi-implications on `sys_open`:

```
(\result >= 3) <==> (dir_lookup(self.dir, 5, pathname) >= 0)
(\result == -1) <==> (dir_lookup(self.dir, 5, pathname) < 0)
```

Expanded to four implications, exactly TWO are FALSE body theorems — the path-completeness
OVER-CLAIM the campaign record flagged:

- (a) `\result >= 3 ==> dir_lookup >= 0`  — SOUND (open succeeds only on a resolvable name)
- (b) `dir_lookup >= 0 ==> \result >= 3`  — **FALSE**: a RESOLVABLE name still returns -1 on
      ENFILE (`_alloc_fd` returns -1 when the 64-slot fd table is full) or permission denial.
- (c) `\result == -1 ==> dir_lookup < 0`  — **FALSE** (the same ENFILE counterexample: -1 with
      a resolvable name).
- (d) `dir_lookup < 0 ==> \result == -1`  — SOUND (an unresolvable name fails regardless of the
      fd table; this is the ENOENT direction `formal_os_enoent` depends on).

The retirement DROPS the two false directions (b),(c) and KEEPS (a),(d) as body-proven
ensures, plus restates (b) in the HONEST FREE-SLOT-CONDITIONED form (the sys_dup precedent):

```
# (a) forward resolution (body-proven)
ensures \result >= 3 ==> dir_lookup(self.dir, 5, pathname) >= 0
# fd->inode binding on success (kept, body-proven)
ensures \result >= 3 ==> (... self.fd_inode[\result] == dir_lookup(self.dir, 5, pathname))
# (b') REVERSE no-failure, CONDITIONED on a free fd slot at entry (the sys_dup form)
ensures (dir_lookup(\old(self.dir), 5, pathname) >= 0
         and (\exists k: int; 3 <= k and k < 64 and \old(self.fd_open[k]) == 0))
        ==> \result >= 3
# (d) ENOENT discriminant, the SOUND direction (NOT the over-claim)
ensures dir_lookup(self.dir, 5, pathname) < 0 ==> \result == -1
```

The `open` public wrapper (`pure_lib/os/__init__.py`) is updated identically (it had
propagated the same false bi-implications from the trust).

## 2. What was REUSED vs NEW

**100% reuse — ZERO new axiom, ZERO new `val`, ZERO new `#@ proof` citation, ZERO `\trusted`.**

- **(a)/(d)/fd->inode binding**: ride the already-LANDED `dir_scan_result` VALUE marker on
  `_dir_lookup` (`\result == dir_lookup(self.dir, block_num, pathname)`, line ~951;
  `0720.proofs/UnixDirScanValue.{v,lean}`). The in-body sibling stub `self__dir_lookup_2`
  carries `ensures { result = dir_lookup self.dir x0 x1 }`, so `inode_num` is tied to
  `dir_lookup` at the call site — the path->inode direction the SKILL.md gap-note (A.11/A.14)
  said was missing is now SUPPLIED by this landed marker.
- **(b') free-slot reverse**: rides `_alloc_fd`'s body-proven FREE-SLOT==>SUCCESS ensures
  (`(\exists free slot) ==> \result >= 3`, line ~763) + the confined, proof-backed
  `#@ fresh_globals` constructor all-free post-state — the IDENTICAL machinery that retired
  sys_dup's fd-resolution-fidelity.

## 3. Soundness: the `--fun` stub-vacuity finding (honest)

The per-function `--fun` body gate emits siblings as `writes`-less `val` stubs, including
`_alloc_fd`. In that mode the success path can prove vacuously — a FALSE unconditioned reverse
proves Valid. **This is NOT specific to sys_open**: a CONTROL test on the LANDED zero-trust
`sys_dup` shows its analogous false claim ALSO proves in `--fun`. So `--fun` SUCCESS establishes
body CONSISTENCY at the same bar as the accepted sys_dup; it is NOT the falsification vehicle.

The DECISIVE non-vacuity + falsification is at the **`open` wrapper boundary** (sys_open is a
conditioned stub there, no `_alloc_fd` body to collapse):

- conditioned wrapper PROVES: `--fun open` SUCCESS.
- FALSE unconditioned reverse INJECTED at the wrapper (`dir_lookup >= 0 ==> \result >= 3`):
  **FAILS** (Alt-Ergo Timeout 30s / Z3 Unknown 330809 steps) — the conditioned stub genuinely
  does NOT entail the over-claim. This is the ENFILE/ENOSPC reality reflected as RED.

The reverse is body-realized through `_alloc_fd`'s REAL `let` (full emission) + `fresh_globals`
at the driver — the sys_dup pattern, end-to-end.

## 4. Gate evidence

SENTINEL each run: `PYTHONPATH=$PWD/src:$PWD/src/pycsl` + abs venv python →
`pycsl from .../agent-a15584a8745fa616b/src/pycsl` (worktree, NOT main). PYTHONHASHSEED=0.

| Check | Command | Result |
|---|---|---|
| Baseline (trusted) | `--fun unixinodefilesystem__sys_open` (pre-edit) | SUCCESS |
| Gate ×1 | `--fun unixinodefilesystem__sys_open` | SUCCESS |
| Gate ×2 | `--fun unixinodefilesystem__sys_open` (with ENOENT dir) | SUCCESS |
| open wrapper ×2 | `os/__init__.py --fun open` | SUCCESS |
| **Falsification** | inject `dir_lookup>=0 ==> \result>=3` at `open` wrapper | **FAILED** (Timeout/Unknown) — correct |
| Non-vacuity (control) | `1==0` on sys_open `--fun` | Timeout (inconclusive in `--fun`; see §3) |
| Non-vacuity (real) | conditioned wrapper proves; false twin reds | the wrapper pair IS the discriminator |
| Collateral `--fun` | `_alloc_fd`, `_dir_lookup`, `sys_dup` | SUCCESS (all) |
| Formal drivers | `formal_os_{fdchain,fd,enoent,namespace2,roundtrip,rwsize}.py` | SUCCESS (all 6, UNMODIFIED) |
| Exhibit | `0713.py` (fresh_globals milestone) | SUCCESS |
| doc-coherency | `bin/doc-coherency.py --check` | GREEN |

## 5. No relocated trust

```
$ grep -rn '#@ \trusted' pure_lib/os/
ZERO bare \trusted in pure_lib/os/   <-- os fully de-trusted (1 -> 0)
```
Diff adds NO `\trusted`, NO `#@ proof`, NO `axiom`, NO `val`, NO `assume` (only comment lines
documenting the retirement). Net trust DOWN by 1, nothing relocated.

## 6. Corpus byte-diff

No corpus exhibit references `sys_open`/the os contract, and the diff adds NO new axiom
citation — corpus `.mlw` emission is unaffected. The changed os `.mlw` (contract changed) is
the intended diff, not a regression. (`run-reference-tests.sh` aborts at the pre-existing
stdlib-coverage gate — unrelated; verified per-fn + per-driver instead.)

## 7. Files (patch)

- `getting-better/PROPOSAL-sys-open-fd-resolution-1to0.patch` (2 files, +79/-19):
  - `pure_lib/os/UnixInodeFileSystem.py` — `sys_open`: drop `\trusted` + the two false
    `<==>`; add (a) forward, (b') conditioned reverse, (d) ENOENT.
  - `pure_lib/os/__init__.py` — `open` wrapper: same restructure.

## 8. Residual / caveats for the parent re-verify

- The `--fun` body gate is stub-vacuity-limited for the conditioned reverse (§3) — re-verify
  the FALSIFICATION at the `open` wrapper (the real discriminator), exactly as for sys_dup.
- `formal_os_fdchain` theorem (1) `open_existing_yields_valid_fd` is the formal-driver
  consequence; it proves with the UNMODIFIED driver against the conditioned contract (no driver
  edit needed). To make the conditioned reverse the *load-bearing* fact there (rather than
  trivially-true), one MAY add `#@ fresh_globals` to that theorem (verified to still SUCCESS),
  but it is not required and was reverted to keep the patch to 2 files.
- Sound exactly to the degree the LANDED sys_dup retirement is sound — same conditioned form,
  same `_alloc_fd` + `fresh_globals` machinery, same cross-validated `dir_scan_result` marker.
