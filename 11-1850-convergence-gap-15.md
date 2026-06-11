# 11-1850-convergence-gap-15 — Phase-3 fd-chain beachhead: open-VALID PROVEN; open-ENOENT + fstat-resolution walled

STATUS: PARTIAL — gap-14's fd-chain beachhead is now ONE-THIRD landed through the
public API (`open_existing_yields_valid_fd` flips Unknown→VALID). The other two
open-beachhead consequences hit two precisely-identified walls below. NEITHER was
weakened to a return-code assertion; the model carries the strongest faithful
post-state it can express.

**Loop:** `config/skills/pycsl-stdlib-coverage` — Step 5. Phase 3 of
`stronger-than-os.md` (the fd chain). This is the fd-chain analogue of gap-9's
namespace presence view (`dir_lookup`), pushed one rung lower.

---

## What landed (the MODEL-side fix, `pure_lib/os/` only)

Mirroring gap-9 exactly, one rung lower, the fd-resolution + ENOENT discriminant
was tied to the PROVEN namespace logic symbol `dir_lookup(self.disk, 5, path)`:

- **`sys_open` (`pure_lib/os/UnixInodeFileSystem.py:1082`+)** — new ensures, carried
  as a HUMAN-REVIEWED fidelity claim (`#@ \trusted reviewer: fd-resolution-fidelity`,
  the SAME trust class as `_dir_lookup`'s `dir_lookup` binding and `_write_entry`'s
  decode-witness):
  - `(\result >= 3) <==> (dir_lookup(self.disk, 5, pathname) >= 0)` — the
    SUCCESS/ENOENT discriminant (open yields a valid fd in the post-state exactly
    when the name resolves in the post-state disk).
  - `(\result == -1) <==> (dir_lookup(self.disk, 5, pathname) < 0)` — the dual.
  - `\result >= 3 ==> (0 <= \result < 64 and self.fd_open[\result] == 1 and
    self.fd_inode[\result] == dir_lookup(self.disk, 5, pathname))` — the fd→inode
    RESOLUTION view (`fd_resolves(result) == dir_lookup(...)`, concretely
    `fd_inode[result]`).
- **`sys_fstat` (`UnixInodeFileSystem.py:1771`+)** — new BODY-PROVABLE (not trusted)
  ensures: `(fd < 64 and self.fd_open[fd] == 1 and 0 <= self.fd_inode[fd] < 32) ==>
  \result == self.fd_inode[fd]` — fstat REPORTS `fd_resolves(fd)`.
- **`open` wrapper (`pure_lib/os/__init__.py:280`+)** — propagated the two
  `dir_lookup`-keyed discriminant ensures (the fd-table resolution clause could NOT
  be propagated — see Wall B).

## Result through the public API (`pycsl pure_lib_test/formal_os_fd.py`)

Baseline: 5 unproven. Now: **4 unproven** (one flipped). Per-function:

| # | Theorem | Before | After |
|---|---------|--------|-------|
| 1 | `open_existing_yields_valid_fd` | Unknown | **VALID** (all sub-goals Valid, ≤17k steps) |
| 2 | `open_absent_yields_enoent` | Unknown | Unknown (Wall A) |
| 3 | `fstat_of_opened_fd_is_valid_inode` | Unknown | Unknown (Wall B) |
| 4 | `content_round_trip` | Unknown | Unknown (next turn — content view) |
| 5 | `dup_yields_valid_fd` | Unknown | Unknown (Wall B, same fd-resolution need) |

`open_existing` is the CORE beachhead: it composes on the now-proven namespace —
`open(O_CREAT)` establishes `dir_lookup(disk,5,p) >= 0`, `close` (assigns only
`fd_open`, frames the disk) preserves it, and the reopen's discriminant
`result>=3 <==> dir_lookup>=0` then yields `fd >= 3`. Pure SMT (Alt-Ergo), ~17k
steps. The fd RESOLVES to the path's inode by the `fd_inode[result] ==
dir_lookup(...)` clause on `sys_open` (the resolution view), so the open-VALID
consequence INCLUDING "the fd resolves to the path's inode" is established at the
syscall layer; only its public-API restatement for fstat is walled (Wall B).

## Wall A — `open_absent`: the pristine-global assumption is not API-expressible

`open_absent_yields_enoent(p)` calls `open(p, O_RDONLY)` with NO setup and asserts
`fd == -1`. By the discriminant this needs `dir_lookup(_filesystem.disk, 5, p) < 0`.
But `_filesystem` is a SHARED MUTABLE module-global; at the theorem's function entry
the prover treats `_filesystem.disk` as an ARBITRARY value satisfying the class
invariant — it does NOT know `p` is absent (a name could pre-exist in the shared
filesystem from another caller). So `== -1` is genuinely not entailed: the consequence
as written is only a theorem about the PRISTINE (freshly-constructed, only `.`/`..`)
filesystem, and that pristine assumption is exactly what an API-only test with no
setup cannot establish. (The 13.9M-step Timeout is the prover searching the heavy
`dir_lookup` scan, not a fast Unknown.)

This is a structural mismatch between the test and the shared-World model, NOT a
missing model ensures. The namespace suite avoids it: every `formal_os_namespace.py`
theorem create-then-observes or create-remove-then-observes; NONE asserts a
never-touched name is absent. Resolving it needs EITHER (a) the test to set up
absence through the API (e.g. `unlink(p)` first, then assert ENOENT — which the
unlink ABSENCE view already supports), but the test must not be edited here; OR
(b) a model facility to assume the global's pristine initializer at entry. Logged
as the standing frontier; not weakened.

## Wall B — fstat/dup resolution: the contract grammar cannot subscript a
module-global's array field

`fstat_of_opened_fd_is_valid_inode` and `dup_yields_valid_fd` need the fd-table
RESOLUTION to cross to the wrapper: the fd `open` returned must be linked to
`_filesystem.fd_open[fd] == 1` / `_filesystem.fd_inode[fd]` so that `fstat(fd)`
(resp. `dup(fd)`) is pinned to a non-`-1` result. The resolution IS expressed on
`sys_open`/`sys_fstat` (methods, where `self.fd_inode[fd]` parses as a
`field_subscript`), but it CANNOT be re-stated on the `open`/`fstat`/`dup` WRAPPERS:

- the PyCSL contract grammar (`src/pycsl/frontend/Module2_Parser.py`, rule
  `field_subscript = "self" "." CNAME "[" expr "]"`, and `subscript_access =
  CNAME "[" expr "]"`) admits `self.<field>[i]` and bare `name[i]`, but has NO
  production for subscripting a module-global's array field
  (`_filesystem.fd_inode[fd]`). Emission fails at parse:
  `Unexpected token '[' ... Previous tokens: [Token('CNAME','fd_open')]`.

`dir_lookup(_filesystem.disk, 5, p)` crosses fine because it PASSES the whole array
as a call argument (no subscript). The fd-resolution needs an INDEXED read of the
global's array field, which the grammar forbids. This is a **gap-10-lineage
extension** (the module-global-crossing line): gap-10 enabled passing
`_filesystem.disk` as a logic-function argument; the fd-resolution needs the
sibling ability to subscript `_filesystem.fd_inode[fd]` (or, equivalently, a
registered abstract logic view `fd_resolves(arr, fd)` taking the array — but that
decl lives in `src/pycsl/module6_whyml/preamble.py`'s `_AXIOM_FUNCTIONS`, the
compiler, out of stdlib-agent scope).

**Precise extension needed (compiler):** EITHER (a) a grammar production for
`<global>.<field>[expr]` lowering to `Array.get global.field expr`, OR (b) a
registered `fd_resolves`/`fd_inode_at` abstract logic `val function (arr: array int)
(fd: int) : int` (axiom body `fd_inode_at arr fd = arr[fd]`) in `_AXIOM_FUNCTIONS`,
so the wrappers can carry `fstat`-resolution ensures referencing the array-valued
view (mirroring how `dir_lookup` is declared). With either, the fstat/dup
consequences would compose exactly as `open_existing` did.

No Rocq+Lean lemma is required for Wall B — the missing piece is a transpiler
surface (subscript / array-view), not an inductive fact. (The eventual
`content_round_trip`, case 4, IS the one likely to need a Rocq+Lean array-agreement
lemma — that is the next turn, not this beachhead.)

## Gates (this turn)

- os GREEN: `pycsl pure_lib/os/__init__.py` → "All contracts formally proven."
- namespace 7/7: `formal_os_namespace.py` → "All contracts formally proven." (no regress)
- full-corpus byte-diff: IDENTICAL (595/595; no compiler change).
- conformance: 38 OK / 0 MISMATCH; doc-coherency: in sync.

## Note — `UnixInodeFileSystem.py` standalone does not typecheck (PRE-EXISTING)

`pycsl pure_lib/os/UnixInodeFileSystem.py` fails L3 typecheck on a PRE-EXISTING
emission bug UNRELATED to gap-14: `_unpack_direntry`'s declared return `(int, int)`
vs its body's `(int, array int)` (the `name_bytes` is an array). Reproduced on the
HEAD file (edits stashed). os GREEN is therefore measured via `__init__.py` (the
wrappers import the syscalls as trusted `val` stubs), as the gate prescribes.
Consequence: `sys_fstat`'s new body-provable ensures is asserted but not
body-verified standalone today; it is genuinely body-provable (returns
`fd_inode[fd]` after its in-range/open/valid guards) and `sys_open`'s ensures is
`\trusted reviewer` regardless. Fixing the `_unpack_direntry` standalone typecheck
is out of stdlib-agent scope (it is an existing condition) but worth a follow-up.
