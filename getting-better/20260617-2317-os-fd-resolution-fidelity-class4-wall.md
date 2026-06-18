# GAP: the 2 os `fd-resolution-fidelity` trusts are a Class-4 (no-ENFILE) wall

**STATUS: LOGGED GAP — human-gated.** Investigated 2026-06-17 by the
`test-supervise-sl` squeeze loop attempting to retire the 2 directives under the
BINDING extreme-rigor doctrine. Both retirement attempts were EXPERIMENTALLY shown
to regress a previously-green gate; reverted. The TCB stays at 8 bare `\trusted`;
neither was faked or weakened.

## Correction to the prior doc (20260617-0938)
The earlier TCB-debt doc named the two `fd-resolution-fidelity` carriers as
`_check_perm` and `sys_readlink`. That is WRONG. The actual carriers are:

- `pure_lib/os/UnixInodeFileSystem.py:1238` — **`sys_open`**
- `pure_lib/os/UnixInodeFileSystem.py:2192` — **`sys_dup`**

(`grep -nE "trusted reviewer:" pure_lib/os/UnixInodeFileSystem.py` — 6 dirscan +
these 2.) `_check_perm`/`sys_readlink` carry no `\trusted` directive.

## Baseline (measured this run)
- os body gate `UnixInodeFileSystem.py`: **3 residuals** (NOT the "8" the headline
  doc implies — those are the visible SMT gap). The 3 are `sys_rename` (1 Assertion)
  and `_unpack_direntry` (2 Preconditions) — UNRELATED to the fd targets, which are
  currently emitted as trusted `val`s (bodies not verified).
- os `__init__` gate: **1159/0 green**.
- bare `\trusted` directives: **8** (6 dirscan-fidelity + 2 fd-resolution-fidelity).

## The classification: both are Class-4 (genuinely-needs-an-assumption), NOT 1/2/3
The shared property is **no-ENFILE**: "allocation always finds a free fd". This is
FALSE when the 64-slot fd table is full — exactly the Class-4 case the doctrine says
must become an honest PRECONDITION or a logged GAP, never a re-assumed axiom.

### `sys_dup` (line 2192) — the clean isolate
Trusted ensures (line 2191):
`(oldfd < 64 and \old(self.fd_open[oldfd]) == 1) ==> \result >= 3`.
Body returns -1 on `newfd >= 64` (ENFILE) or `newfd == oldfd`. So the ensures is
literally false at table-full. **VERIFIED experimentally:** removing the `\trusted`
and adding the honest preconditions `requires self.next_fd < 64` /
`requires self.next_fd != oldfd` makes the body **fully verify — 46 sub-goals all
Valid, ZERO trust**, including the former-trusted `\result >= 3`. The body retirement
is SOUND and was machine-confirmed.

### `sys_open` (line 1238) — the same wall, compounded
Trusted ensures include the biconditional
`(\result >= 3) <==> (dir_lookup(self.dir, 5, pathname) >= 0)`. This is over-strong
on THREE independent unprovable branches: ENFILE (`if fd >= 64: return -1`),
alloc-fail (`_alloc_inode`/`_dir_find_free` returning -1), and perm-deny
(`if self._check_perm(...) == 0: return -1`). A resolvable name with a full fd table
returns -1, not >= 3 — the `<==>` is false. Retiring it needs preconditions
excluding ALL THREE failure modes, on top of the Class-3 `no_inline` dir_lookup-scan
composition. Far larger blast radius (9+ formal tests open files).

## Why the precondition route REGRESSES (the wall)
`next_fd < 64` is **not establishable through the public API**:

1. It is NOT a maintainable strict class invariant — `sys_open`/`sys_dup`/`sys_creat`
   each do `fd = next_fd; if fd >= 64: return -1; next_fd = fd + 1`, so the strongest
   maintainable invariant is `next_fd <= 64` (non-strict). At `next_fd == 64` dup MUST
   return -1; no invariant rescues the success direction.
2. No public op EXPOSES or BOUNDS `next_fd`, so a caller/formal-test cannot establish
   `next_fd < 64` at the call site after an `open` (open's contract does not pin
   next_fd's post-value).

**Measured regression** (with `sys_dup` precondition added, `__init__` propagated):
- `__init__` gate stayed 1159/0 green ONLY because it imports `sys_*` as trusted
  `val`s and does not re-check the wrapper's call-site preconditions (the os-gate
  blind spot — bodies not verified there).
- but the public-API FORMAL TESTS red:
  - `pure_lib_test/formal_os_fd.py`: green→FAILED, 2× `Precondition of
    dup_yields_valid_fd` (the new `next_fd < 64` / `!= fd` undischargeable at the
    `dup(fd)` call site).
  - `pure_lib_test/formal_os_fdchain.py`: green→FAILED, 4× (`dup_of_valid_source_is_valid`,
    `dup_shares_inode` preconditions).
  Both confirmed GREEN before the change by stashing the os edits and re-running
  (atomic stash+pop; `git stash list` empty after).

Per the binding doctrine ("removing a `\trusted` that reds a gate is a REGRESSION →
revert + GAP"), both edits were REVERTED. os body gate back to 3 residuals,
`__init__` 1159/0, trusted count 8. No dangling stash.

## ROOT CAUSE — a model limitation, not just an SMT wall
The model uses a **monotonic `next_fd` counter with NO fd reuse** (close does not
free a slot for reallocation). So after 61 total opens `next_fd == 64` and the table
is "full" even if every fd was closed. Faithful Unix allocates the LOWEST free fd,
so a closed fd is reusable and "no-ENFILE given a free slot" is a real, derivable
property. With the current monotonic model, no-ENFILE is genuinely unprovable for any
non-trivial open/close sequence — the trust is papering over the missing fd-reuse
semantics.

## The doctrine-compliant retirement (substantial, human-gated)
To retire BOTH without regressing the public tests:
1. Replace the monotonic `next_fd` with a **free-fd allocator** (`_alloc_fd()` scans
   `fd_open[3..64)` for the first closed slot, returns -1 only when ALL 64 are open).
2. Add a maintained class invariant counting open fds (or simply: the allocator's
   ensures `\result == -1 or (3 <= \result < 64 and fd_open[\result] == 0)`).
3. Then `sys_dup`/`sys_open` success becomes conditional on `(open-fd count) < 64`,
   an invariant a formal test CAN establish (it opened/closed a bounded, known set of
   fds). `dup`/`open` retirement then has zero trust and the public tests still prove.
This is a faithful-semantics upgrade (fd reuse) the `unix` skill endorses, not a
convenience hack. Effort: moderate (one new leaf + an occupancy invariant + caller
re-proof). Lower urgency than functional frontiers; it is the real ceiling on an
"os fully validated under extreme rigor" claim for the fd subsystem.

## NOT acceptable (struck from the option set)
- Keeping the bare `\trusted` as a "win" (it IS the debt).
- Re-assuming no-ENFILE as a cited axiom about an abstract `next_fd` symbol — that is
  FALSE (table-full is reachable), so it would surface as a kernel `Axiom` and be a
  REJECT, AND it would assert a falsehood.
- A precondition that reds the public formal tests (measured regression above).
