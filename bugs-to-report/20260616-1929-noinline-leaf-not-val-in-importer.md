# `#@ no_inline` on a module-level codec leaf may not be honored as a `val` in an importing gate

**STATUS: UNCONFIRMED** (suspected from a run interrupted by machine load; needs a
clean repro).

**Symptom.** A module-level codec leaf (`_unpack_direntry` in
`pure_lib/os/UnixInodeFileSystem.py`) was given a byte-range precondition
(`#@ for i in range(0,32): requires 0 <= data[i] <= 255`) plus `#@ no_inline`,
mirroring the proven `_unpack_inode`. In **isolation** (`--fun _unpack_direntry`)
and in the standalone body gate the change was clean (leaf 35/0; body gate 8→4).
But the **importing gate** `pure_lib/os/__init__.py` (which imports
`UnixInodeFileSystem`) became dramatically slower — **>25 min without finishing vs
~15 min** before — and the emitted `__init__.mlw` still contained the leaf's
byte-range clauses (the `255` count was unchanged after adding `no_inline`),
suggesting the leaf's **body is still being verified** in the importer's context
rather than treated as a contract-only `val`.

**Expected.** `#@ no_inline` should make the leaf a `val` (contract only, body
verified once standalone) in any importing context — so its 32-clause precondition
adds no body-VC / E-matching cost to the `__init__` gate.

**Actual (suspected).** The importing gate appears to re-verify the leaf's body, so
the extra precondition clauses inflate `__init__`'s axiom-rich VC and stall it.

**Minimal repro (to run on an unloaded machine).**
1. On `pure_lib/os/UnixInodeFileSystem.py`, add to `_unpack_direntry`:
   `#@ for i in range(0,32): requires 0 <= data[i] <= 255` and `#@ no_inline`.
2. `PYTHONHASHSEED=0 … -m pycsl pure_lib/os/__init__.py` — time it; inspect whether
   `_unpack_direntry`'s body VCs appear in the run.
3. Compare against the same with `_unpack_direntry` left unchanged.

**What would confirm.** A clean (unloaded) timing showing the `no_inline` leaf's
body VCs present in the `__init__` run, and the slowdown reproducing deterministically.
If confirmed, it is a real `no_inline`-across-import limitation; if not, the
slowdown was machine load and this entry is closed.

**Context.** Surfaced while fixing the genuine `_unpack_direntry` leaf-precondition
residual (the leaf calls `_unpack_uint16_be(data,0)`, whose `0<=data[0..1]<=255`
preconditions its own `\valid(data,32)` cannot discharge). The fix was reverted to
protect the `__init__` gate; a minimal 2-clause precondition (only `data[0..1]`) is
the proposed lower-perturbation retry.
