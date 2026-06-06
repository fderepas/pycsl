# Verified `open` in `my_os.py`: 4 OS errors + valid-fd postcondition, non-opaque, 0 `\trusted`

## Context

Prior task (byte round-trip `_block_roundtrip`) is **COMPLETE** — see git/notes. New
task: annotate `open` in `unix-filesystem/my_os.py` so it provably raises exactly
**FileNotFoundError** (ENOENT), **PermissionError** (EACCES/EPERM), **FileExistsError**
(EEXIST), **IsADirectoryError** (EISDIR), and on success returns a handle to a valid
file open in the filesystem. Change `open`'s body so the 4 errors actually occur.

User's chosen rigor (via clarifying Qs): **`open` is a fully-verified METHOD whose
`self` IS the filesystem (modeled, non-opaque); the path is a non-opaque byte array;
existence / is-dir / permission are DERIVED-and-PROVEN from real disk + inode state**
(not supplied as opaque inputs); also **strengthen `sys_open`** to prove the success fd
is genuinely open; **the whole `my_os.py` must verify** with **0 `\trusted`**; the
runtime demo must still work.

Two facts shape the design:
- A free function over the module-global `_fs` singleton **cannot be meaningfully
  verified** — `_fs`/`_fs.x` emit abstract `val` ops and pass *vacuously*
  (`expressions.py:776-810`). The proven pattern for "self == modeled object" is a
  **self-contained single-file class** (cf. corpus 0427 `Echo`, 0428 `RoundTrip`).
- **Cross-file inheritance is unsupported** — `Module5_IREmitter.py:1065 visit_ClassDef`
  never reads `node.bases`; a record's fields come only from *this* class's `__init__`.
  So `class MyOS(UnixInodeFileSystem)` would emit an empty record. The class must
  re-declare its own fields.

## Approach

`my_os.py` becomes the **verified surface**: a self-contained `class MyOS:` (no base)
re-declaring the modeled fields + class invariants and carrying the verified `open`
method plus the few helpers it needs. The **runtime glue** (`_fs` singleton, `import
os/sys`, the thin `os`-mimicking free functions) moves to a new **`my_os_runtime.py`**
that is *not* fed to pycsl; the demo imports that. This is the only robust way to get
"the whole `my_os.py` verifies meaningfully" — every body in it operates on the modeled
`self`, so there is no abstract-op escape.

### Modeled `self` + non-opaque byte path
```
#@ class invariant \length(self.disk) >= 131072
#@ class invariant \length(self.fd_open) == 64        (+ fd_inode/fd_offset/fd_flags)
#@ class invariant self.next_fd >= 3
class MyOS:
    def __init__(self):
        self.disk: list = bytearray(131072)
        self.fd_open/fd_inode/fd_offset/fd_flags: list = [0]*64
        self.next_fd = 3
        self._format_disk()
```
A path is a **30-byte `array int`** (`requires \length(name) == 30`) — the dirent name
slot. Name equality reuses the existing `\array_eq` (explicit forall) over 30-byte
`Array.sub` slices. Inode num is read arithmetically (`disk[off]*256+disk[off+1]`), name
slots written via `Array.blit` — both keep content prover-known (no opaque
`struct.unpack`). O_EXCL = 128 added as a class constant (O_CREAT=64 already exists);
inode layout: index 2 = type (1=file, 2=dir), 3 = mode.

### The verified `open` (raise guards mirror each `when` verbatim → `C→C` VCs)
```
#@ requires \length(name) == 30 and flags >= 0
#@ assigns self.disk, self.fd_open, self.fd_inode, self.fd_offset, self.fd_flags, self.next_fd
#@ raises FileNotFoundError  when self._dir_lookup_bytes(5, name) < 1 and bit_and(flags,64) == 0
#@ raises FileExistsError    when self._dir_lookup_bytes(5, name) >= 1 and bit_and(flags,64) != 0 and bit_and(flags,128) != 0
#@ raises IsADirectoryError  when self._dir_lookup_bytes(5, name) >= 1 and self._read_inode(self._dir_lookup_bytes(5, name))[2] == 2
#@ raises PermissionError    when <resolved, non-dir, and mode bits forbid the access implied by bit_and(flags,3)>
#@ ensures \result >= 3 and self.fd_open[\result] == 1
```
Body: ordered `if <guard>: raise …` in the same order; O_CREAT path allocates inode
(type 1, mode 420) + links a 30-byte entry, then re-lookups; success sets
`fd_open[fd]=1` and returns `fd` (`fd=next_fd>=3`, bounds-checked `fd<64`). Because
`_dir_lookup_bytes`/`_read_inode` are `assigns \nothing`, the `when`-clause re-invocation
equals the body local (referential transparency) — so each raise-site VC is `C→C`,
trivial. This holds **independently of** how strong `_dir_lookup_bytes`'s functional spec
is; the strong spec only buys *meaning* ("derived from real state"), not the VC.

### `sys_open` strengthening (trivial)
`ensures \result == -1 or (\result >= 3 and self.fd_open[\result] == 1)` — discharged by
the `fd_open[fd]:=1; return fd` store (Array.set read-back) + `next_fd>=3` + `fd<64`. No
new invariant. (Mirror onto `sys_dup`/`sys_dup2` optionally.)

### The one hard VC + fallback ladder
`_dir_lookup_bytes`'s **positive** functional postcondition
`\result >= 1 -> \exists j<16. \array_eq(slot_j, name) and ino_j == \result` is an ∃∀
shape Alt-Ergo/Z3 will likely time out on across the 16-iteration loop. Ladder (take the
first that holds; **none uses `\trusted`**):
1. **Baseline (ship this):** prove only the **universal / not-found** direction
   `\result == -1 -> \forall j<16. not \array_eq(slot_j, name) or ino_j == 0` (+ result
   bounds). This monotone universal E-matches cleanly and **soundly underwrites a raised
   FileNotFoundError** (if we report absent, it really is absent). The four raise VCs and
   `is_dir`/`perm` derivations need only this + `assigns \nothing`.
2. If the existential is required: add `#@ proof rocq UnixFs.Dir.lookup_found_witness`
   for that one ensures, with a real `.v` lemma (induction over the 16-step scan) +
   register its axiom in `module6_whyml/preamble.py` `_AXIOM_REGISTRY` — same honest
   pattern as the existing `i18`/`i1a1` round-trips and `bit_and_one_in_zero_one`.
3. If even the universal's nested 30-elt forall stresses SMT: hoist name-equality into a
   helper `_name_eq(...) -> int` with `ensures \result == 1 <-> \array_eq(...)` so the
   loop invariant references a single-level predicate.

**Every corpus test for this feature must run under the `hoare` memory model** — under
other models `\array_eq` emits `true` and the spec is vacuous.

### Exception model
**No change required.** `raises X when C` does *not* validate names against
`KNOWN_EXCEPTIONS` (only `no_exception` does); a plain `raise FileNotFoundError` in the
body declares the WhyML exception via `collect_user_exceptions`. Phase 0 confirms this
empirically. *Contingency only:* if some path rejects the names, add the 4 to
`KNOWN_EXCEPTIONS` in both `src/pycsl/exception_model.py` and
`src/self-annotate/src/exception_model.py` (cheap, no TRIGGERS entry needed).

## Phases (each independently `pycsl.py`-verifiable; each adds a corpus test, `hoare` model)

0. **Substrate + exception check** — `0429.py`: self-contained class (no base), modeled
   `disk`/`fd_*` + invariants, a single `open(self, name: list, flags)` with the 4 plain
   `raise`s + `raises … when …` + `ensures \result == -1 or \result >= 3`, inlined byte
   lookup. Confirms: 4 OS exceptions verify with no exception-model change; byte path +
   modeled self verify; raise-site `C→C` discharges. Gate: SUCCESS, 0 trusted.
1. **`_dir_lookup_bytes` unit** — `0430.py`: the 16-entry byte scan in isolation with the
   **not-found universal** ensures (ladder rung 1) + result bounds + per-slice memory
   safety. Gate: SUCCESS.
2. **Found direction (optional/escalation)** — `0430b`/extend: attempt the existential in
   pure SMT; if it stalls, add the Rocq citation (rung 2). Document which rung shipped.
3. **Integrated `MyOS` in `my_os.py`** — rewrite `my_os.py` to the self-contained class:
   fields+invariants, copied helpers (`_set_bitmap`,`_get_bitmap`,`_alloc_inode`,
   `_alloc_block`,`_read_inode`,`_write_inode`,`_format_disk`,`_write_entry_bytes`,
   `_dir_lookup_bytes`), the verified `open`, `O_*`+`O_EXCL`. No module-level `_fs`, no
   free functions. Corpus mirror `0431.py`. Gate: `pycsl.py unix-filesystem/my_os.py` →
   SUCCESS, **0 `\trusted`**.
4. **Strengthen `sys_open`** in `UnixInodeFileSystem.py` to the `fd_open[\result]==1`
   ensures (+ optional dup/dup2). Gate: `pycsl.py unix-filesystem/UnixInodeFileSystem.py`
   → SUCCESS, still 0 trusted; `--audit-proof` 18/18.
5. **Relocate runtime glue + wire demo** — new `unix-filesystem/my_os_runtime.py` holds
   `_fs`, constants, the `os`-mimicking free functions (bodies lifted verbatim; can
   encode a str path → 30-byte buffer and call the verified `MyOS.open` so the 4 errors
   occur at runtime too). `my_os_demo.py`: `import my_os` → `import my_os_runtime as
   my_os` (1 line). Gate: `python3 unix-filesystem/my_os_demo.py` → `round-trip OK`.

## Critical files
- `unix-filesystem/my_os.py` — rewritten into the verified `MyOS` class (Phase 3).
- `unix-filesystem/my_os_runtime.py` — NEW runtime glue, not pycsl-fed (Phase 5).
- `unix-filesystem/my_os_demo.py` — 1-line import switch (Phase 5).
- `unix-filesystem/UnixInodeFileSystem.py` — `sys_open` ensures strengthening (Phase 4);
  source of the helper bodies to copy.
- `src/pycsl/module6_whyml/preamble.py` — only if ladder rung 2 (Rocq citation) is needed
  (`_AXIOM_REGISTRY`).
- `test-suite/corpus/pycsl-reference/0429–0431.py` — NEW tests (clone 0428's shape; run
  under `hoare`).
- (contingency) `src/pycsl/exception_model.py` + `src/self-annotate/src/exception_model.py`.

## Verification
- Per phase: `.venv/bin/python3 src/pycsl/pycsl.py <file>` (corpus tests under the `hoare`
  model) → "Verification SUCCESS", exit 0.
- Final: `pycsl.py unix-filesystem/my_os.py` → SUCCESS, `grep -c '\trusted reviewer:'` ==
  0, `MyOS.open` emits as `let` (body-verified) with the 4 `raises` + `ensures \result
  >= 3 and self.fd_open[\result]==1`; `pycsl.py unix-filesystem/UnixInodeFileSystem.py`
  → SUCCESS + 0 trusted + `--audit-proof` 18/18; `cmmi-audit.sh` `[STRUCT]` 0
  trusted-only / 0 unknown; `python3 unix-filesystem/my_os_demo.py` → `round-trip OK`;
  broad corpus regression unaffected.
- Report which fallback rung shipped for `_dir_lookup_bytes`, and state plainly that the
  literal cross-call `my_os_test` round-trip remains out of scope (unchanged boundary).
