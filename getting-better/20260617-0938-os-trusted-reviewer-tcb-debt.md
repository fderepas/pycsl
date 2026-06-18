# GAP: pre-existing `\trusted reviewer:` directives in the os model (TCB debt)

**STATUS: LOGGED GAP — human-gated (per the binding extreme-rigor doctrine).**
Surfaced 2026-06-17 while verifying the cheap-wins mission (grepping for trust).

## What
`pure_lib/os/UnixInodeFileSystem.py` carries **8 `#@ \trusted reviewer:` directives** —
reviewer-asserted, with **no machine proof**. They make the annotated function's body
*trusted* (emitted as a `val` whose contract is assumed, body not verified):

- **`dirscan-fidelity` ×6** — the directory-scan helpers: `_read_directory`,
  `_dir_lookup`, `_dir_find_slot`, `_dir_find_free`, `_write_dir_entry`,
  `_write_entry`. They assume the concrete 16-slot block scan faithfully realizes the
  abstract `dir_lookup` / `slot_inode` / `slot_name` model.
- **`fd-resolution-fidelity` ×2** — `sys_open` and `sys_dup` (the no-ENFILE / fd
  allocation direction the model cannot currently derive). *(Corrected 2026-06-18: an
  earlier draft of this line named `_check_perm`/`sys_readlink` — wrong; those carry
  no `\trusted`. The real carriers are `sys_open` (line 1238) and `sys_dup` (2192).
  See `20260617-2317-os-fd-resolution-fidelity-class4-wall.md`.)*

(`__init__.py` only *references* these in a comment; the wrappers are `val`s with no
`\trusted` directive of their own.)

## Why it matters
A `\trusted reviewer:` directive is exactly the form the **extreme-rigor doctrine
forbids going forward** (a raw TCB addition with no machine proof — see
`test-supervise-sl.md` §Doctrine, the BINDING rule). These **predate** the doctrine,
so they are not a violation by any loop — but they mean that *"fully validate os
under extreme rigor"* is **not** just "close the 8 SMT residuals". The true target is
**TCB = the cited, dual-prover cross-validated axiom set only** (e.g. the Bitmap
family), with **zero `\trusted reviewer:`** body-trusts. Today the os TCB is larger
than that headline suggests.

## The work (per directive — doctrine-compliant routes only)
For each, either:
1. **Prove** the assumed property in **Rocq AND Lean**, cross-validate, and bind it
   back via `#@ proof rocq … / #@ proof lean …` so the body becomes verified (the
   directive is deleted). For `dirscan-fidelity`, the existing
   `unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan*` lemmas
   already prove pieces of the scan↔model correspondence — the work is to compose
   them in-context so the helper's body discharges. **OR**
2. **Restructure** the helper (leaf-first contracts / folded atoms / a reformulation)
   so SMT discharges its body without the trust.

A reviewer `\trusted` swap is **never** an acceptable resolution (it *is* the debt).
If neither route closes a directive, it stays a logged GAP, and the decision to keep
a TCB item is **the human's**, not a loop's.

## Effort / priority
Substantial and per-directive (each is a proof or a restructure). Lower urgency than
the functional frontiers (reopen-by-name, multi-block), but it is the **real ceiling**
on an "os is fully validated under extreme rigor" claim — the 8 SMT residuals are the
visible gap; these 8 trusts are the invisible one.
