# 20260623-1440-slice-write-type-invariant-isolation.md

**Ergonomics gap surfaced during:** the 20260623 UnixInodeFileSystem body-VC squeeze.

## Problem

A `sibling_concrete` helper that writes `self.dir`/`self.disk` via a loop (e.g.
the former `_blit_dir_entry`, 30 individual byte writes) generates a
type-invariant maintenance VC **per write** (uniq / slots_lt32 / inode_bytes_valid).
Each VC needs the slot-specific `dir_blit_marker` fold to discharge, but the helper
only knows the opaque byte offset `off`, not the slot index — so the marker fold
can't fire, and the VCs time out (27.9B–131.7B steps at 120s).

The caller (`_write_dir_entry`) knows the slot and cites the marker, but
`sibling_concrete` isolates the helper's body VC from the caller's fold — the
caller's marker discharges the caller's postcondition, NOT the helper's
type-invariant VCs.

## Workaround applied

Restructured the helper to build the entry in a **local array** (zero
class-invariant VCs on the loop) + a **single slice write** (1 type-invariant VC
instead of 30). This reduced `_blit_dir_entry` from 4 timeouts to 2 and
`_blit_disk_entry` from 4 to 1. The residual type-invariant VCs (the single
slice write's uniq/inode_bytes_valid maintenance) still can't discharge without
the slot index.

## Proposed feature

**Option A — `sibling_concrete` type-invariant forwarding.** Let a
`sibling_concrete` helper's type-invariant VCs be discharged by the CALLER's
context (which knows the slot and cites the marker). This would let the helper's
body VC inherit the caller's marker fold, closing the residual VCs. Semantically
sound (the helper IS inlined into the caller at the SMT level for
`sibling_concrete`); the type-invariant VC should be checked at the call site,
not in isolation.

**Option B — `#@ type_invariant_off` directive.** A directive that suppresses
per-write type-invariant VCs for a helper whose caller maintains the invariant
via an explicit marker fold. The helper would carry an annotation like
`#@ type_invariant_maintained_by_caller` and its body VC would skip the
uniq/slots_lt32/inode_bytes_valid checks (the caller's fold is the proof).

Either option would convert the 3 remaining `_blit_*` type-invariant GAPs to
Valid without any new axiom or `\trusted`.
