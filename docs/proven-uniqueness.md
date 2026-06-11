# Proven directory uniqueness — out of the TCB

This document explains, in detail, how the `pure_lib/os` model's
**directory-uniqueness** property is now *genuinely proven* rather than *trusted*,
and why that change shrinks the [trusted computing base](glossary/trusted-computing-base.md)
(TCB). It is a record of a real result — commit `2e37a9a`, the gap-13 closure —
documented from the actual code (`pure_lib/os/UnixInodeFileSystem.py`), the axiom
registry (`docs/glossary/axiom-registry.md`), and the dual-kernel proof companion
(`docs/glossary/proof-companion.md`).

The short version: a property that the verifier used to *believe* (a human-reviewed
`\trusted` ensures) is now a machine-checked **class invariant** that Why3 forces
every mutator to re-establish. What was assumed is now derived; what remains trusted
is strictly smaller and strictly more local.

---

## 1. What directory uniqueness *is*

The `os` model stores the root directory in **block 5** of its virtual disk — the
512-byte region `[2560, 3072)`, laid out as 16 fixed-size 32-byte directory entries
("dirents"), each a `(inode, name)` pair following the Unix on-disk layout (a name
lives only in a dirent and maps to an inode number; the inode itself never holds the
name). A slot is **live** when its inode field decodes to a nonzero inode number.

> **Directory uniqueness:** no two *distinct* live slots in block 5 decode to the
> same name.

Why the filesystem needs it. Uniqueness is the property that makes a *name* behave
like a name:

- **A name resolves to at most one inode.** Path resolution
  (`_dir_lookup` / `_dir_find_slot`) scans the 16 slots for a matching live name. If
  two live slots could share a name, "the inode for `d`" would be ambiguous.
- **Removing a name truly makes it absent.** `rmdir` / `unlink` zero the *one* slot
  the lookup found. If a duplicate could exist, clearing one slot would leave the
  name still resolvable — `unlink(d)` would not make `d` absent, and the
  remove-reflects-absence consequence (`stronger-than-os.md`, Phase 1) would be false.

In the model the invariant is stated over the registry's abstract decode symbols
`slot_inode` / `slot_name` (`UnixInodeFileSystem.py`, the active
`#@ class invariant` at line ~472):

```python
#@ class invariant \forall i: int; \forall j: int;
#@   (0 <= i < 16 and 0 <= j < 16
#@    and slot_inode(self.disk, 5, i) != 0 and slot_inode(self.disk, 5, i) < 32
#@    and slot_inode(self.disk, 5, j) != 0 and slot_inode(self.disk, 5, j) < 32
#@    and slot_name(self.disk, 5, i) == slot_name(self.disk, 5, j)) ==> i == j
```

This is the same property the absence proof (`remove_reflects_absent`, gap-11) needed
as a hypothesis: at most one live slot decodes to a given name, so zeroing the slot a
lookup returned makes the name absent.

---

## 2. How it *was* trusted (the starting point)

Before gap-13, uniqueness lived in the TCB as a `\trusted` postcondition on
`_dir_find_slot` — the helper that scans block 5 for the slot holding a given name.
Alongside the (still-trusted) decode-fidelity clauses — that the returned slot is live
(`slot_inode != 0`) and decodes to `pathname` (`slot_name == pathname`) — it
**asserted** that no *other* live slot decodes to the same name:

```text
\forall k != \result. slot_name(self.disk, block_num, k) == pathname
                       ==> slot_inode(self.disk, block_num, k) == 0
```

This claim was *true*. Every directory adder rejects a name that already exists —
`mkdir` and `link` return `EEXIST`, `open` with `O_CREAT` and `symlink` likewise
reject a duplicate — so no reachable disk ever holds two live slots with the same
name. But under `#@ \trusted` the claim was **unproven**: it was a *global structural
assertion read off the disk at lookup time*, accepted on human review. The SMT backend
never checked it; it entered every VC as a believed fact. It sat in the TCB under the
`trustedContractsAxiom` line ("functions annotated `\trusted` satisfy their stated
contracts"; see [trusted-computing-base](glossary/trusted-computing-base.md) §1).

The weakness was not that the claim was *false* — it is true — but that it was
*global and only believed*. Trusting "the directory has no duplicate names" means
trusting a property of every reachable disk state, asserted at one read site, with
nothing forcing the *writers* to keep it true. A code change that introduced a
duplicate-admitting write path would not have been caught: the lookup's trusted ensures
would have continued to assert uniqueness regardless.

---

## 3. How it is *now* proven

Gap-13 replaces the trusted assertion with a **maintained class invariant** on
`UnixInodeFileSystem`. A Why3 type/class invariant is a proof obligation, not a belief:
the [weakest-precondition VC generator](glossary/verification-condition.md) demands that
the invariant **hold of every constructed value** and be **re-established by every
method that mutates the object** (`assigns self.disk`). The SMT solvers (Alt-Ergo
2.6.2, Z3 4.13.3) discharge those obligations. Three pieces close the proof.

### 3.1 Established — vacuously, on the zeroed disk

The constructor builds `self.disk = bytearray(131072)` — in WhyML, `Array.make 131072
0`. The invariant must hold of that witness. Because every byte of block 5 is zero,
every slot's inode field decodes to `0`: every slot is *dead*, so there is no live
pair and the `==> i == j` body is vacuously satisfied. SMT cannot see this on its own
(`slot_inode` is an abstract `val function`, so a zeroed array tells it nothing about
the decode), so the establishment is discharged by the cited cross-validated axiom
**`UnixFs.Dir.empty_disk_slots_dead`** (a zeroed block-5 region decodes to all-16-slots
dead). This is the antecedent-discharge dual of `slot_inode_nonneg`. It collapses the
`unixinodefilesystem'vc` type-invariant witness and the `_filesystem` module-global
precondition VCs from *Unknown* to *Valid*.

### 3.2 Maintained by the directory adders — via `insert_preserves_unique`

The seven directory mutators (`sys_mkdir`, `sys_rmdir`, `sys_link`, `sys_unlink`,
`sys_rename`, `sys_symlink`, `sys_creat`) write block 5 through `_write_entry`. The
**adders** make one slot live with a name; they must re-prove uniqueness afterward.
They cite **`UnixFs.Dir.insert_preserves_unique`**: from a disk with no duplicate live
names, making one slot live with a name *not already live* (their EEXIST /
duplicate-rejection guard supplies "not already live"), while every other slot is
unchanged, preserves no-duplicate-live-names. The hypotheses are supplied by the
syscall's own duplicate-rejection check plus `_write_entry`'s **slot-locality frame
ensures** — that the write changes only the target slot's decode and leaves every
other slot's `slot_inode` / `slot_name` equal to its `\old` value:

```python
#@ ensures \forall k: int; (0 <= k < 16 and k != slot)
#@   ==> slot_inode(self.disk, block_num, k) == \old(slot_inode(self.disk, block_num, k))
#@ ensures \forall k: int; (0 <= k < 16 and k != slot)
#@   ==> slot_name(self.disk, block_num, k)  == \old(slot_name(self.disk, block_num, k))
```

### 3.3 Maintained by the removers — directly

`rmdir` / `unlink` zero a slot (`_zero_entry`). Clearing a slot only *shrinks* the live
set, so no new duplicate can appear; the invariant is preserved with no axiom — the
remover side needs nothing cited.

### 3.4 Preserved by the non-directory writers — for free, via a decode frame

A class invariant obligates **every** `assigns self.disk` method, not just the
directory ops. The non-directory syscalls (`chmod`, `chown`, `utimensat`, `write`,
`truncate`, `ftruncate`, `open`) write the disk — but never block 5. Naively, each
still has to re-prove the block-5 uniqueness invariant over the abstract decode after
its write; that ballooned (the gap-13 `chmod` VC timed out at 30 s / 232M steps over
the uninterpreted `slot_inode`).

The fix is a **decode-locality frame**. These syscalls write the disk *only* through a
small set of helpers — `_write_inode`, `_set_bitmap`, `_alloc_inode`, `_alloc_block`,
`_block_roundtrip` — each of which writes a region provably disjoint from block 5's
bytes `[2560, 3072)` (the inode region `[512, 2560)`, the bitmap blocks below 2560, or
data blocks `>= 3072`). Each helper carries a **block-5 decode-frame ensures** (every
block-5 slot's decode equals its `\old` value) that its body proves from the byte-level
disjointness of its `Array.blit` via the cited **`UnixFs.Dir.block5_decode_frame`** —
two disks that agree on `[2560, 3072)` have equal block-5 decode at every slot. For
example, `_write_inode`:

```python
#@ proof rocq UnixFs.Dir.block5_decode_frame
#@ proof lean UnixFs.Dir.block5_decode_frame
#@ ensures \forall k: int; (0 <= k < 16) ==> slot_inode(self.disk, 5, k) == \old(slot_inode(self.disk, 5, k))
#@ ensures \forall k: int; (0 <= k < 16) ==> slot_name(self.disk, 5, k)  == \old(slot_name(self.disk, 5, k))
def _write_inode(self, inode_num, inode):
    offset = 512 + (inode_num * 64)
    self.disk[offset:offset + 64] = _pack_inode(inode)
    #@ assert \forall b: int; (2560 <= b < 3072) ==> self.disk[b] == \old(self.disk[b])
```

`_set_bitmap` additionally carries a write-locality `#@ requires` (the written byte
`byte_offset + bit_index // 8 < 2560`) so its disjointness from block 5 is provable;
every caller passes a system-block bitmap offset, so the precondition holds. With the
decode-frame on the helpers, the seven non-directory syscalls inherit uniqueness
maintenance with **zero body annotation** — the timeout collapses to a one-line
rewrite.

### 3.5 The trusted uniqueness ensures is removed

With establishment + maintenance proved end-to-end, the `\trusted` uniqueness ensures
on `_dir_find_slot` was **deleted**. Uniqueness now *follows from the maintained class
invariant*: because the invariant holds in every reachable state, and `_dir_find_slot`
returns a live slot named `pathname` (its two still-trusted decode-fidelity clauses),
the invariant forces every *other* live slot named `pathname` to coincide with the
result. The callers that relied on the old ensures (`sys_unlink`, `sys_rename`) now
derive uniqueness from the active invariant with a one-line `#@ assert`. The header
comment on `_dir_find_slot` records the change ("UNIQUENESS — PROVEN, OUT OF THE TCB
(gap-13)").

---

## 4. The six cross-validated `UnixFs.Dir.*` axioms it rests on

The proof leans on the `UnixFs.Dir.*` family in the
[axiom registry](glossary/axiom-registry.md) — **six** axioms, each cited by paired
`#@ proof rocq` / `#@ proof lean` directives and each proved **offline in both Rocq and
Lean** under the dual-kernel discipline of the [proof companion](glossary/proof-companion.md):

| Axiom | Role | Shape |
|---|---|---|
| `scan_reflects_present` | PRESENCE reflection: `dir_lookup >= 0 ↔ ∃ live slot named name` | inductive over the 16-slot scan (SMT times out — gap-9) |
| `remove_reflects_absent` | ABSENCE reflection: after the live slot is zeroed and `name` lived only there, `dir_lookup < 0` | same prefix induction (gap-11) |
| `insert_preserves_unique` | INSERT-side **maintenance** of the uniqueness invariant (§3.2) | finite 4-way case split, no induction (gap-12) |
| `empty_disk_slots_dead` | EMPTY-DISK **establishment**: zeroed block-5 region → all 16 slots dead (§3.1) | byte-local decode rewrite (gap-13) |
| `block5_decode_frame` | DECODE-LOCALITY **frame**: disks agreeing on `[2560,3072)` have equal block-5 decode (§3.4) | byte-local decode rewrite (gap-13) |
| `slot_inode_nonneg` | unsigned-byte fact: a decoded inode field is non-negative | the non-negativity antecedent the others need |

The three load-bearing for uniqueness are the last three of the gap-12/gap-13 work:
`insert_preserves_unique` (maintenance by the adders), `empty_disk_slots_dead`
(vacuous establishment), and `block5_decode_frame` (free preservation by the
non-directory writers), with `slot_inode_nonneg` discharging the non-negativity
hypotheses.

Each axiom passes the registry's [trust model](glossary/axiom-registry.md#trust-model),
enforced by `audit_proof.py`:

- **Rocq:** `coqc` exit 0, `Print Assumptions` *Closed under the global context* (only
  the proofs' abstract Section Variables; no `Axiom`, no `Admitted`).
- **Lean:** `lake env lean` exit 0, `#print axioms` a subset of the kernel allowlist
  (`{propext, Quot.sound}` for these), no `sorry`.

The proofs live in
`unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/` as matched
`.v` / `.lean` pairs (`EmptyDiskSlotsDead`, `Block5DecodeFrame`,
`InsertPreservesUnique`, `UnixDirScan{,Absent}`). The cross-check halts on
disagreement and **never picks a winner** — a fact earns trust only as a pair accepted
by *both* independent kernels, guarding against a single assistant's soundness bug. The
SMT backend then instantiates each axiom via E-matching to discharge the relevant VCs;
neither Rocq nor Lean runs during a routine `pycsl` proof (their guarantees are banked
offline in the audited companion).

---

## 5. Why it matters for the TCB

This is the point of the result. Uniqueness moved **from a trusted, human-reviewed
global assertion into a machine-checked proof.**

### The TCB shrank

Before, the TCB contained the *global, structural* claim "the directory has no
duplicate live names," believed on review via the `\trusted` ensures on
`_dir_find_slot`. That claim is now **derived**, not assumed. Why3's WP VC generator
produces it from:

1. the maintained class invariant (re-established on **every** mutator by the SMT
   solver), and
2. the six `UnixFs.Dir.*` axioms, each independently checked by **two** proof-assistant
   kernels.

What remains trusted is strictly smaller and strictly more local: only the **narrow,
byte-level `dirscan-fidelity` decode-vs-bytes clauses** — that `_dir_lookup` /
`_dir_find_slot` / `_write_entry` read and write the right bytes of a single dirent
(`slot_inode == pathname`'s decode side, `_write_entry`'s slot-locality write) — plus
the six dual-kernel axioms. These are *local* (about one slot's 32 bytes, or a
byte-region frame) and *cross-validated by two kernels*, where the old trusted claim
was *global* (about every reachable disk) and *checked by neither solver nor a kernel*.
A reviewer auditing a 32-byte decode fidelity clause has a far smaller, more concrete
obligation than a reviewer asked to believe a global structural invariant of all
reachable directory states.

### Checked, not believed

The decisive difference is *enforcement*. A `\trusted` ensures is **believed** — the
solver takes it as a hypothesis and never tests it; nothing constrains the writers to
keep it true. A proven class invariant is **checked on every mutator**: the VC
generator forces each `assigns self.disk` method to re-establish uniqueness, and the
SMT backend (with the cited axioms) must discharge that obligation, or the module fails
to verify.

The operational consequence: **a future code change that broke uniqueness would now
fail to verify, rather than silently violate a trusted claim.** If someone added a write
path that admitted a duplicate name, the maintenance VC for that method would no longer
discharge — the proof would go red. Under the old trusted ensures, `_dir_find_slot`
would have continued to assert uniqueness regardless, and the defect would have passed
silently. This is the same TCB-reduction discipline the VCG chain followed
(see [trusted-computing-base](glossary/trusted-computing-base.md) §"How the TCB is being
reduced"): replace a broad believed axiom with a proved theorem plus a narrower,
better-stated residual trust.

---

## See also

- [axiom registry](glossary/axiom-registry.md) — the `UnixFs.Dir.*` family and the trust model
- [proof companion](glossary/proof-companion.md) — the dual-kernel Rocq + Lean cross-validation
- [trusted computing base](glossary/trusted-computing-base.md) — the TCB inventory and reduction discipline
- [class invariant](glossary/class-invariant.md) — how Why3 establishes and maintains object invariants
- `stronger-than-os.md` — the functional-consequence program that motivated the namespace model
