# GAP: `dirscan-fidelity` ×6 retirement is SMT-INFEASIBLE — a structural wall (the uninterpreted byte↔slot bridge)

**STATUS: LOGGED GAP — confirmed-hard, human-gated (per the binding extreme-rigor doctrine).**
Produced 2026-06-17 by the `test-supervise-sl` squeeze loop attacking the
`dirscan-fidelity` TCB debt (mission target of
`getting-better/20260617-0938-os-trusted-reviewer-tcb-debt.md`).

## Bottom line
The 6 `#@ \trusted reviewer: dirscan-fidelity` directives in
`pure_lib/os/UnixInodeFileSystem.py` (`_dir_lookup`, `_dir_find_slot`,
`_dir_find_free`, `_write_dir_entry`, `_write_entry`, `_zero_entry`) **cannot be
retired** by either sanctioned route (a Rocq+Lean cross-validated `#@ proof`, or a
no-trust restructure) **with the model as it stands.** Removing any one of them reds
the body gate. **Net TCB delta: 0 (6 → 6).** Nothing was retired; nothing was
weakened, faked, or trusted-away. This is the same class of wall as the documented
`sys_rename` no-trust infeasibility — and it is reported as a SUCCESS of the mission
(an honest, pinned structural finding), not a failure.

## The wall, precisely
The three abstract symbols the directives' contracts bind to —
`slot_inode (disk: array int) (blk k: int) : int`,
`slot_name (disk: array int) (blk k: int) : string`,
`dir_lookup (disk: array int) (blk: int) (name: string) : int` — are declared in the
WhyML preamble (`src/pycsl/module6_whyml/preamble.py:771-774`) as **`val function`,
i.e. fully UNINTERPRETED**. Every axiom that mentions them
(`preamble.py:123-575`: `scan_reflects_present`, `slot_inode_nonneg`,
`dir_lookup_present_witness`, `remove_reflects_absent`, the frame/uniqueness family,
`empty_disk_slots_dead`, …) is **purely relational** — it constrains how these
symbols relate to *each other* (presence ⇔ existential, frame-on-disjoint-write,
uniqueness, nonneg, all-dead-on-zeroed-block). **There is NO axiom anywhere that
DEFINES `slot_inode disk blk k` as a function of the concrete bytes**
(`disk[blk*512 + k*32 .. +2]` big-endian, the `_unpack_direntry` decode).

That missing definitional axiom is *exactly* the property each `dirscan-fidelity`
directive assumes: "the concrete 16-slot byte scan faithfully realizes
`slot_inode` / `slot_name` / `dir_lookup`." The helper bodies compute over real bytes
(`_unpack_direntry`, `_pack_direntry`, byte slices); their contracts relate the result
to the uninterpreted symbols. With no bridge axiom, the bodies provably **cannot**
discharge the fidelity ensures — there is no logical path from the bytes to the
opaque symbol.

## Why the cross-validated lemmas do NOT close it (route a blocked)
The existing `unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan*`
lemmas prove the **scan STRUCTURE** (the loop ⇔ the existential): `UnixDirScan.v`
declares `slot_inode`/`slot_name` as Coq `Variable`s (abstract) and proves
`scan_reflects_present` for **any** such decode (its own comment: *"the model leaves
slot_inode / slot_name uninterpreted … the reflection property holds for ANY such
decode"*). The proofs **deliberately abstract away the very byte↔slot bridge** that
the trust assumes. To use route (a) one would have to:
1. give `slot_inode` a CONCRETE byte-decode definition, and
2. prove (in Rocq AND Lean) that the helper body computes exactly that decode.
But the on-disk encoded byte CONTENT is **opaque by design** (Gap 5: `_pad_name` /
`.encode()` bytes are not value-modeled — only `str` itself is the Why3
`string.String` value type). There is no faithful concrete `slot_name`/`dir_lookup`
definition to prove against — even in a proof assistant — because the bytes carrying
the name are unmodeled. So route (a) is blocked at its root, not merely unproved.

## Why the no-trust body does NOT prove (route b blocked) — measured
**Pilot — `_dir_find_free`** (simplest: read-only, single ensures
`\result >= 0 ==> slot_inode(self.dir, 5, \result) == 0`):
- `--fun unixinodefilesystem___dir_find_free --no-typecheck` with the trust REMOVED:
  the postcondition appeared **Valid** in isolation — but this was a **fragile
  empty-disk artifact**, not a sound discharge. Triangulation:
  - `== 0` Valid, `== 1` Valid, `== 7` Timeout, `== 999` (contradicts the `< 16`
    range) Timeout → context is consistent (999 fails) yet small constants pass: a
    performance/instantiation artifact off the canonical zeroed `by{}` witness, NOT a
    real proof of the fidelity claim.
  - **Soundness probe (decisive):** add `#@ requires slot_inode(self.dir, 5, 0) == 3`
    (force slot 0 LIVE). The `== 0` postcondition then **Timeout / FAILS** — proving
    the isolated pass relied on the empty-disk assumption, not on the body.
- **FULL body gate** (`pycsl pure_lib/os/UnixInodeFileSystem.py --no-typecheck`,
  PYTHONHASHSEED=0, ~12 min) with `_dir_find_free` de-trusted: the
  `_dir_find_free` Postcondition goes **Out of memory (15.21s)** — UNPROVEN. The gate
  goes RED (was green with the trust). Per the doctrine HARD CONSTRAINT, removing a
  `\trusted` that reds a gate is a REGRESSION, not a retirement → directive STAYS.

**Confirmation — `_write_entry`** (a write-side helper): de-trusted,
`--fun unixinodefilesystem___write_entry`, its fidelity postconditions
(`slot_inode == inode_num`, `slot_name == name` after a byte write) go
**Unknown / Timeout / Out of memory** even in isolation — no empty-disk artifact even
masks it, because writing bytes cannot establish the uninterpreted symbol's value.

## The other five share the wall (not ground individually — provably identical)
Per the PROCEDURE's "pin reality / don't grind once the wall is structural": all six
bind to the SAME three uninterpreted symbols across the SAME missing bridge:
- `_dir_lookup` → `\result == dir_lookup(self.dir, 5, pathname)` (read-side value bind)
- `_dir_find_slot` → `slot_inode != 0 ∧ slot_name == pathname` (read-side live bind)
- `_dir_find_free` → `slot_inode == 0` (read-side free bind) — PILOTED, OOM
- `_write_dir_entry` → `slot_inode == inode_num ∧ slot_name == name` (write-side, `self.dir`)
- `_write_entry` → same (write-side, `self.disk`) — CONFIRMED Unknown/Timeout/OOM
- `_zero_entry` → `slot_inode == 0` after a zero-write (write-side absence bind)
Each needs the identical byte↔slot definitional axiom that does not exist and cannot
be faithfully written under Gap 5. Retiring any one reds the gate.

## What WOULD retire them (the real, human-gated work — not a loop's to take)
A faithful close requires giving `slot_inode`/`slot_name`/`dir_lookup` a **concrete
definitional axiom** over the disk bytes (`slot_inode disk blk k = unpack_uint16_be(disk, blk*512+k*32)`,
and an analogous decode for `slot_name`/`dir_lookup`), cross-validated in Rocq AND
Lean, then proving each helper body computes it. This is blocked TODAY by Gap 5 (the
name byte-content is unmodeled, so `slot_name`/`dir_lookup` have no faithful concrete
form). It is therefore a **substantial model extension** (value-model the directory
name bytes → define the three symbols concretely → cross-validate → rebind), gated on
the human, exactly like the `sys_rename` and `chmod/truncate-consequence` frontiers.

## Gates (both green on the restored, byte-clean tree)
- `pure_lib/os/UnixInodeFileSystem.py` (body gate): unchanged from baseline
  (2016 Valid / 8 residual, dirscan helpers trusted) — `git diff` empty after the
  experiment was reverted.
- `pure_lib/os/__init__.py` gate: re-confirmed green (see the run alongside this doc).

## Evidence trail (reproducible)
- `slot_inode`/`slot_name`/`dir_lookup` decls: `preamble.py:771-774` (`val function`).
- No byte-bridge axiom: grep of `preamble.py` for `slot_inode` shows only relational
  axioms (lines 123-575); none is `slot_inode … = <Array.get/unpack …>`.
- Rocq abstraction: `UnixInodeFileSystem.proofs/rocq/UnixDirScan.v:27-33` (`Variable
  slot_inode`, `Variable slot_name`).
- Pilot OOM in the full gate: `_dir_find_free` Postcondition Out of memory (15.21s).
- Write-side wall: `_write_entry` Postcondition Unknown/Timeout/OOM in `--fun`.
