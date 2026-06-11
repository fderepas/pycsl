# 11-2325-convergence-gap-17 — STDLIB/TEST-AGENT gap: the dir_lookup namespace frame across write

**Loop:** `config/skills/pycsl-stdlib-coverage` convergence loop, gap-17 (the os content
round-trip `write→read==len(data)`, per spec-16's named keystone). Module: `pure_lib/os/`.

## Context — gap-17 is landing brick by brick

The content round-trip's size linkage is being threaded THROUGH THE PUBLIC API. Committed
(HEAD `8718e6d`): the read side — a DEFINED logic function `inode_size(disk, ino)` (the
be32 decode of the inode SIZE field, zero trust / zero registry axiom), `_read_inode`
exposes `\result[0] == inode_size(...)`, and `sys_read`/`read()` return `min(nbytes, size)`.
Plus `sys_lseek`/`lseek()` SEEK_SET offset post-state. os GREEN 1229 VCs, corpus byte-identical.

On disk (this turn's WIP): the write side. `UnixFs.Dir.lookup_frame` is registered in
`_AXIOM_REGISTRY` (cross-validated Rocq+Lean — `LookupFrame.{v,lean}`, Rocq Closed under
global context, Lean axioms ⊆ {propext, Quot.sound}). `sys_write` exports, all BODY-PROVEN:
- `inode_size(disk, fd_inode[fd]) >= len(data)` (the SIZE post-state),
- the bounded slot-decode frame `\forall k; 0≤k<16 ⟹ slot_inode/slot_name(disk,5,k)==\old(...)`,
- the namespace frame `\forall q:str; dir_lookup(disk,5,q) == \old(dir_lookup(disk,5,q))`,
via the p_block guard fixed to `< 6` (every data write lands at ≥3072, disjoint from dir
block 5 [2560,3072)) + a block-5 byte-frame loop invariant + `block5_decode_frame` +
`lookup_frame`. **`sys_write`'s VC proves in isolation.**

## THE GAP — two symptoms, one root cause: the global `lookup_frame` axiom

Citing `UnixFs.Dir.lookup_frame` to discharge `sys_write`'s namespace frame emits it as a
**module-global** Why3 `axiom`, in scope for EVERY goal in the file. Its antecedent is
`( forall k. 0 ≤ k < 16 → slot_inode d1 5 k = slot_inode d0 5 k )` (and the slot_name twin).
That pattern matches the slot-frame `#@ assert`s that the OTHER block-5-touching syscalls
already carry — so the solver instantiates `lookup_frame` on goals that have nothing to do
with name resolution, and E-matches itself into the ground.

### Symptom 1 — REGRESSION: `chmod'vc` Assertion Timeout (was Valid at baseline)
`sys_chmod` (`pure_lib/os/UnixInodeFileSystem.py`) carries, to maintain the directory-
uniqueness class invariant, the asserts:
```
#@ assert \forall k: int; (0 <= k and k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
#@ assert \forall k: int; (0 <= k and k < 16) ==> slot_name (self.disk, 5, k) == \old(slot_name (self.disk, 5, k))
```
These are exactly `lookup_frame`'s antecedent shape. With the axiom globally in scope the
solver fires it (matching d1:=disk, d0:=\old disk) and then chases the conclusion
`dir_lookup disk 5 name = dir_lookup (\old disk) 5 name` for unconstrained `name`, blowing up:
**Timeout 30.00s, 4 036 053 steps** (full `pycsl pure_lib/os/__init__.py`). chmod does NOT
need a dir_lookup frame at all. (Same family of E-matching blowup the gap-9 scan axiom hit;
there it was isolated with `no_inline`.)

### Symptom 2 — `write'vc` Postcondition Unknown: the wrapper frame won't propagate
The public `write()` wrapper (`pure_lib/os/__init__.py`) must re-export the namespace frame
`\forall q; dir_lookup(_filesystem.disk,5,q) == \old(dir_lookup(_filesystem.disk,5,q))` so a
caller (the content round-trip test) can carry `A := dir_lookup(disk,5,p)` across
write→close→reopen. The wrapper body is the bare delegation `return _filesystem.sys_write(...)`,
so the frame should copy directly from `sys_write`'s identical post — but the solver does not
instantiate the universal across the call: **Unknown, 389 796 steps**. (Confirmed it is the
`\old(dir_lookup …)` propagation, not the quantifier: a single concrete-name probe
`dir_lookup(disk,5,"probe")==\old(...)` is ALSO Unknown at the wrapper.) Note: a `--fun write`
probe is MISLEADING here — `--fun` trusts callees as bare `val`s with NO contract, so the
wrapper sees no `sys_write` post at all; only the FULL run is diagnostic.

## Minimal reproducer
```
pycsl pure_lib/os/__init__.py     # 1236 Valid, 2 unproven: chmod'vc Timeout, write'vc Unknown
```

## Root cause (file:line)
- `src/pycsl/module6_whyml/preamble.py` `_AXIOM_REGISTRY["UnixFs.Dir.lookup_frame"]` — the
  axiom is emitted with NO E-matching trigger, so it instantiates on every `forall k. slot_*`
  fact in the module (chmod's frame asserts), not only where a `dir_lookup` frame is actually
  being proved.
- The `write()` wrapper cannot instantiate `sys_write`'s universal `\forall q` (or even a
  concrete-name) namespace frame across the call boundary without the axiom firing on the
  goal's `dir_lookup` terms.

## Proposed fix (for the tool-agent's spec)
Give `UnixFs.Dir.lookup_frame` an explicit **multi-pattern E-matching trigger** on the pair of
`dir_lookup` applications in its conclusion, so it fires ONLY when a genuine dir_lookup-frame
goal is present (both `dir_lookup d1 5 name` and `dir_lookup d0 5 name` occur — the write
wrapper's frame goal), and NEVER on a bare slot-frame assert (chmod, which has no dir_lookup
pair):
```
forall d0 d1 name [dir_lookup d1 5 name, dir_lookup d0 5 name].
  ( forall k. 0 ≤ k < 16 → slot_inode d1 5 k = slot_inode d0 5 k ) ->
  ( forall k. 0 ≤ k < 16 → slot_name  d1 5 k = slot_name  d0 5 k ) ->
  dir_lookup d1 5 name = dir_lookup d0 5 name
```
Expected: chmod's slot-frame asserts no longer trigger the axiom (no dir_lookup pair) → chmod
back to Valid; the write wrapper's frame goal has both dir_lookup terms → the axiom fires with
d1:=post, d0:=\old, discharging the antecedents from `sys_write`'s bounded slot-frame post →
`write'vc` Valid. Confirm the os byte-diff (corpus byte-identical: lookup_frame is emitted only
where cited, and the trigger is inside the cited axiom body), os GREEN (1229 + the gap-17 frame
VCs, 0 unproven), and the cross-check (`bin/check-proof-crosscheck.sh`) still maps the citation
to the `LookupFrame.{v,lean}` proofs.

## Gate (independent, by the coordinator)
- [ ] `pycsl pure_lib/os/__init__.py` → 0 unproven (chmod Valid, write Valid).
- [ ] byte-diff sweep both-ways vs HEAD preamble → corpus byte-identical.
- [ ] `\trusted` count unchanged (7); no new bare SMT skip.
- [ ] proof cross-check green for `UnixFs.Dir.lookup_frame`.
