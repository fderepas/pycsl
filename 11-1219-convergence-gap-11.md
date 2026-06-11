STATUS: OPEN — SMT WALL on the ABSENCE direction of the directory-scan reflection (inductive over the 16 slots); to be closed by TWO cross-validated Rocq + Lean axioms the next TOOL-AGENT must register in `src/pycsl/module6_whyml/preamble.py` (skill Step 5b). The PRESENCE direction (4 of 7 namespace consequences) is now CLOSED through the public API; the 3 ABSENCE consequences stay Timeout, blocked on the lemmas named in §Lemma. os kept GREEN at **1480/0** (`#@ no_inline` + entry-write-last on `sys_link`/`sys_rename`).

# Convergence gap — iteration 11 (namespace ABSENCE: `rmdir`/`unlink`/`rename`-old → `access` ABSENT walls on the reverse `dir_lookup < 0` direction; the scan-reflects-ABSENCE proof needs a remove-witness + a scan-uniqueness lemma, both inductive over `range(16)`)

**Loop:** `config/skills/pycsl-stdlib-coverage` — Step 5 / Step 5b.
**Predecessors:**
- `11-0605-convergence-gap-7.md` (§A: os namespace consequences were return-code-only through the public API; the prescribed fix is an observable presence view a mutator establishes and an observer reflects).
- `11-0743-convergence-gap-9.md` + `11-1039-convergence-gap-10.md` (the PRESENCE beachhead: `mkdir`/`access` ensures bound to `dir_lookup(disk,5,name) >= 0` via the cross-validated `UnixFs.Dir.scan_reflects_present` IFF; the forward existential `=>` direction discharges from a written-slot witness).
**Iteration:** N = 11.

## What landed (the PRESENCE direction — CLOSED through the public API)

The two remaining PRESENCE consequences now prove VALID through the public `os` API, exactly mirroring `mkdir`'s beachhead:

- `pure_lib/os/UnixInodeFileSystem.py` `sys_link` (~L1073): added `#@ ensures \result == 0 ==> dir_lookup(self.disk, 5, newpath) >= 0`, the four `#@ proof rocq/lean UnixFs.Dir.{scan_reflects_present,slot_inode_nonneg}` cites, and the final-slot existential `#@ assert`. Body REORDERED so the link-count bump (`_write_inode`) runs BEFORE `_write_entry`, making the entry write LAST (mkdir's shape); marked `#@ no_inline`.
- `pure_lib/os/UnixInodeFileSystem.py` `sys_rename` (~L1357): added `#@ requires oldpath != newpath`, `#@ ensures \result == 0 ==> dir_lookup(self.disk, 5, newpath) >= 0`, the four cites, the existential `#@ assert`; marked `#@ no_inline`.
- `pure_lib/os/__init__.py` wrappers `link` (~L161) and `rename` (~L292): propagated `#@ ensures \result == 0 ==> dir_lookup(_filesystem.disk, 5, dst) >= 0` (and `rename`'s `#@ requires src != dst`).

**Why `#@ no_inline` was load-bearing.** Without it, the prover inlines `sys_link`/`sys_rename` whole — including the loop-bearing `_dir_find_free`/`_dir_find_slot` scans — and the final existential witness assert E-matching-explodes (Timeout, 7.5M–251M steps; os regressed to 10 unproven goals). `no_inline` isolates the witness VC (the call-site only sees the ensures), and entry-write-last keeps the `slot_inode`/`slot_name` witness in the immediate pre-assert state. With both, os is GREEN at **1480/0** and the wrapper ensures discharge.

## Where it WALLED — the ABSENCE direction (3 consequences, precisely pinned)

`rmdir_then_access_absent`, `unlink_then_access_absent`, `rename_then_a_absent` require the DUAL post-state ensures:
- `sys_rmdir`/`sys_unlink` (on success): `dir_lookup(self.disk, 5, pathname) < 0` (the name is GONE after zeroing its dirent slot).
- `sys_rename`: additionally `dir_lookup(self.disk, 5, oldpath) < 0` (old name gone).

Running the STANDARD gate `pycsl pure_lib_test/formal_os_namespace.py` after the PRESENCE landing, the per-function Postcondition verdicts are:

| Consequence | Postcondition | Result |
|-------------|---------------|--------|
| `mkdir_then_access_present`  | `\result == 1` | **Valid** (1800 steps) |
| `file_present_after_mkdir`   | `\result == 1` | **Valid** (1772 steps) |
| `link_then_b_present`        | `\result == 1` | **Valid** (1829 steps) — *flipped Timeout→Valid* |
| `rename_then_b_present`      | `\result == 1` | **Valid** (1829 steps) — *flipped Timeout→Valid* |
| `rmdir_then_access_absent`   | `\result == 0` | **Timeout** (30 s, 14.35M steps) |
| `unlink_then_access_absent`  | `\result == 0` | **Timeout** (30 s, 13.98M steps) |
| `rename_then_a_absent`       | `\result == 0` | **Timeout** (30 s, 80.37M steps) |

**Root cause.** The reverse `dir_lookup < 0` direction of `scan_reflects_present` (antecedent `slot_inode_nonneg` discharged) is:
```
dir_lookup disk_after 5 name < 0  <->  forall k. 0<=k<16 ->
    NOT (slot_inode disk_after 5 k <> 0 /\ slot_inode disk_after 5 k < 32 /\ slot_name disk_after 5 k = name)
```
To establish that `forall k` after the body zeroes the matching slot `s` (`disk[2560 + s*32 : +32] = b'\x00'*32`), the proof needs THREE facts the model CANNOT currently express:

1. **remove-witness** — zeroing slot `s` makes `slot_inode disk_after 5 s == 0` (the slot is now dead). The existing `_write_entry`/`slot_inode`/`slot_name` axioms pin only the WRITE side of a LIVE entry; there is no logic fact relating a zeroed 32-byte dirent slice to `slot_inode == 0`.
2. **scan-uniqueness** — at most one live slot in block 5 decodes to a given `name` (else removing one leaves another that still matches). `sys_mkdir` rejects duplicate names, so this is TRUE of every reachable disk, but it is a directory INVARIANT (no two live slots share a name), inductive over the 16 slots, never stated.
3. **slot-locality** — zeroing slot `s` leaves every OTHER slot `k != s`'s decode unchanged (`slot_inode`/`slot_name` at `k` are functions of the bytes of slot `k` only). A frame fact about the abstract per-slot decode.

All three are INDUCTIVE/quantified over `range(16)`; SMT times out exactly as the forward scan did (gap-9). They are the ABSENCE twin of the PRESENCE `scan_reflects_present` valve and must be cross-validated in Rocq + Lean and registered, NOT discharged by Z3.

**Boundary note (why this agent could not close it).** Registering a new `#@ proof rocq/lean` axiom requires adding its body to `_AXIOM_REGISTRY` in `src/pycsl/module6_whyml/preamble.py` — citing an unregistered qualname is a HARD `PyCSLIRError` (`#@ proof <qn>: not in Module6 axiom registry`). The STDLIB-AGENT edit boundary is `pure_lib/os/` only (NEVER `src/pycsl/`), so the absence lemmas cannot be introduced from the model side. This is the convergence handoff to the TOOL-AGENT.

## §Lemma — what the TOOL-AGENT must register

Add to `unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan.{v,lean}` and register in `src/pycsl/module6_whyml/preamble.py::_AXIOM_REGISTRY`:

1. `UnixFs.Dir.remove_reflects_absent` (the consolidated absence reflection, the cleanest single registration):
   ```
   forall disk : array int. forall blk : int. forall name : string. forall s : int.
     ( forall j : int. 0 <= j < 16 -> slot_inode disk blk j >= 0 ) ->
     ( 0 <= s < 16 ) ->
     ( slot_inode disk blk s = 0 ) ->                               (* slot s now dead — remove-witness *)
     ( forall k : int. 0 <= k < 16 -> k <> s ->
         slot_name disk blk k = name -> slot_inode disk blk k = 0 ) ->  (* uniqueness: name lived only at s *)
     dir_lookup disk blk name < 0
   ```
   Provable in Rocq/Lean by the same `scan_reflects_prefix` induction already in `UnixDirScan.v` (the reverse `<-` of the IFF + the two hypotheses make the existential witness set empty). Closed under the global context / `{propext, Quot.sound}`, same trust class as `scan_reflects_present`.

2. **scan-uniqueness as a maintained directory INVARIANT** (the model side of hypothesis 2): the `UnixInodeFileSystem` class invariant `\forall i j. (0<=i<16 /\ 0<=j<16 /\ live_i /\ live_j /\ slot_name 5 i = slot_name 5 j) ==> i = j`, established by `_format_disk` and preserved by every `_write_entry` (because `sys_mkdir`/`sys_open`/`sys_link`/`sys_rename` only write a name not already present). NOTE: this is itself inductive over the 16 slots; expect it to need a registered `UnixFs.Dir.scan_unique` companion (or to be folded into `remove_reflects_absent`'s third hypothesis discharged at the call site from the `_dir_find_slot` result). The TOOL-AGENT should pick whichever keeps os's per-VC count green.

Once registered, `sys_rmdir`/`sys_unlink`/`sys_rename` cite `remove_reflects_absent`, supply the remove-witness `#@ assert slot_inode(self.disk, 5, slot) == 0` after the zeroing slice, and add `#@ ensures \result == 0 ==> dir_lookup(self.disk, 5, pathname) < 0`; the wrappers `rmdir`/`remove`/`unlink`/`rename` propagate it, and the 3 ABSENCE consequences flip Timeout→Valid — completing all 7/7 through the public API.

## Gates (this iteration)

- STANDARD `pycsl pure_lib_test/formal_os_namespace.py`: **4/7 VALID** (mkdir/file-present/link-b/rename-b), **3/7 Timeout** (rmdir/unlink/rename-a absence), per the table above. (Was 2/7 Valid at gap-10.)
- `pycsl pure_lib/os/__init__.py`: **1480/1480 VALID, 0 unproven** — `[+] Verification SUCCESS`. (PRESENCE ensures on link/rename discharged in-body via `no_inline` + entry-write-last.)
- `bin/byte-diff-sweep.sh` before/after: **IDENTICAL** (595 reference-corpus .mlw, 0 changed — only `pure_lib/os/` touched).
- Conformance: **38 OK / 0 MISMATCH**; determinism 10/10.
- doc-coherency `bin/doc-coherency.py --check`: **green** (48 directives in sync; acceptance-syntax in sync).
