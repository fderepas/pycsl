STATUS: OPEN

# Convergence gap — iteration 7 (os namespace consequences won't prove through the PUBLIC API: syscall contracts expose NO observable post-state)

**Loop:** `config/skills/pycsl-stdlib-coverage` — Step 5 rules "a formal test must
verify the operation's CONSEQUENCE, not merely call it" and "a formal test CALLS the
public API under test — it must NEVER re-implement or simulate the operation."
**Surfaced by:** the test-agent, rewriting `pure_lib_test/formal_os_namespace.py` from
its previous SIMULATED form (local `disk=[0]*64`, hand-written dirent bytes, inlined
`_dir_lookup`) into honest, API-only setup→operate→observe scenarios.
**Iteration:** N = 7.
**Relation to prior gaps:** this is gap-4 §4a re-surfacing **HONESTLY through the real
public API** (the previous os formal tests hid it behind a simulation). It is the same
root cause; this doc re-states it from the API-caller's seat and adds the `stat`
str/int stub-typing friction (§B) that the rewrite hit.

## Summary

The rewritten `formal_os_namespace.py` calls ONLY the public os API (`mkdir`, `rmdir`,
`unlink`, `link`, `rename`, `access`, `F_OK`) and asserts each namespace
operation's functional CONSEQUENCE on the observed post-state:

| Theorem | Scenario (API only) | Consequence asserted | Result |
|---------|---------------------|----------------------|--------|
| `mkdir_then_access_present` | `mkdir(d)` → `access(d, F_OK)` | `== 1` (PRESENT) | **Unknown** (0.09s, 186713 steps) |
| `rmdir_then_access_absent` | `mkdir(d)`;`rmdir(d)` → `access(d, F_OK)` | `== 0` (ABSENT) | **Unknown** (0.10s, 186711 steps) |
| `unlink_then_access_absent` | `mkdir(f)`;`unlink(f)` → `access(f, F_OK)` | `== 0` (ABSENT) | **Unknown** (0.07s, 186711 steps) |
| `file_present_after_mkdir` | `mkdir(f)` → `access(f, F_OK)` | `== 1` (PRESENT) | **Unknown** (0.08s, 186529 steps) |
| `link_then_b_present` | `mkdir(a)`;`link(a,b)` → `access(b, F_OK)` | `== 1` (b PRESENT) | **Unknown** (0.07s, 184000 steps) |
| `rename_then_b_present` | `mkdir(a)`;`rename(a,b)` → `access(b, F_OK)` | `== 1` (b PRESENT) | **Unknown** (0.06s, 184000 steps) |
| `rename_then_a_absent` | `mkdir(a)`;`rename(a,b)` → `access(a, F_OK)` | `== 0` (a ABSENT) | **Unknown** (0.08s, 184000 steps) |

Every theorem EMITS cleanly and every other VC (the preconditions, the early-return
branches) is **Valid** — only the single consequence postcondition per theorem is
Unknown. That is the honest API-boundary answer: **the os syscalls' public contracts
say nothing that links a name a mutator writes to what an observer later reads under
that name.** This is the correct convergence-loop outcome (a documented Unknown), NOT a
licence to simulate or to weaken to the observer's own return-code disjunction.

## §A — Minimal API-only reproducer (the make-or-break consequence)

```python
from pure_lib.os import mkdir, access, F_OK

#@ requires True
#@ ensures \result == 1
def mkdir_then_access_present(d: str) -> int:
    rc = mkdir(d, 0o777)          # the REAL syscall
    if rc != 0:
        return 1
    return access(d, F_OK)        # the REAL observation — Unknown (0.06s, 186713 steps)
```

There is no internal access here: it imports the public `mkdir`/`access`/`F_OK` and
calls them as any caller would. The postcondition `\result == 1` (d is PRESENT after
mkdir) is **Unknown**.

### Root cause (cite the PUBLIC contracts, `pure_lib/os/__init__.py`)

The mutator and the observer each expose ONLY a return-code `ensures`; neither relates
to the other's state:

- `mkdir`  (`__init__.py:290-295`): `#@ ensures \result == 0 or \result == -1` — does
  NOT ensure that after success the name `d` becomes observable.
- `access` (`__init__.py:113-122`): `#@ ensures \result == 0 or \result == 1` — does
  NOT ensure that a just-created name reads back as present.
- `rmdir`/`unlink`/`link`/`rename` (`__init__.py:300-302, 257-259, 155-158, 286-288`):
  all `#@ ensures \result == 0 or \result == -1` — pure return-code, no post-state.

So in the WhyML the emitted `val access (filepath: string) (mode: int) : int` returns a
value constrained only to `0 || 1`, with no functional dependence on the disk state
`mkdir` mutated. The solver therefore sees `access(d, F_OK)` as an unconstrained `0/1`
and cannot discharge `== 1`. (This is gap-4 §4a's `_dir_lookup` name-byte opacity, but
the gap is now stated where it actually bites a CALLER: the *public contract* exposes
no post-state, regardless of how the body resolves names internally.)

## §B — Secondary friction: `stat`/`lstat` un-annotated path param ⇒ emitted `int`, unusable as a str observer

The natural observer for `link`/`rename` PRESENT (it returns an inode number, exposing
the hard-link shared-inode identity) is `stat`/`lstat`. But their `filepath` param is
left un-annotated in the model:

- `stat`  (`__init__.py:307`): `def stat(filepath, *, ...)` — no type.
- `lstat` (`__init__.py:314`): `def lstat(filepath, *, ...)` — no type.

PyCSL's emitted stub types the un-annotated param `int` (`val stat (filepath: int) : int`),
so passing a symbolic `str` name — `stat(b)` for `b: str` — is a **WhyML type error at
emission** ("This expression has type string, but is expected to have type int"),
before any proof runs. Consequence for the test-agent: of the namespace observers, only
`access` is str-typed, so it is the ONLY API observer through which a name-keyed
consequence is even expressible. The shared-inode hard-link identity (`stat(a)==stat(b)`)
is therefore not statable through the API at all today — even setting aside §A.

## Proposed fix (MODEL side — a stdlib-agent task next turn; this doc is NOT a tool gap)

This is a **model-contract gap**, not a tool bug: PyCSL discharged every VC its inputs
justified, and correctly returned Unknown where the contracts are silent. The fix is to
strengthen the os MODEL's syscall `ensures` to expose the post-state an observer reads —
NOT to weaken the test and NOT to touch `src/pycsl/`. Concretely:

1. **Post-state linkage (the §A fix).** Give the namespace syscalls a post-state the
   observers' contracts can read. The cleanest shape that matches the World architecture:
   model a name→presence relation (or the inode-table presence) as observable state, and
   have each syscall `ensures` it:
   - `mkdir(d)` on success ⇒ `access(d, F_OK) == 1` (d becomes present);
   - `rmdir(d)`/`unlink(d)` on success ⇒ `access(d, F_OK) == 0` (d becomes absent);
   - `link(a, b)` on success ⇒ `access(b, F_OK) == 1` and `b` shares `a`'s inode;
   - `rename(a, b)` on success ⇒ `access(a, F_OK) == 0` and `access(b, F_OK) == 1`.
   This requires the underlying `sys_*` contracts (and `_dir_lookup`'s name-byte codec,
   gap-4 §4a / gap-6) to carry the written name forward — the deeper byte-codec
   round-trip wall those gaps describe. Until that lands, `access` after a mutator stays
   Unknown.
2. **Annotate `stat`/`lstat`'s `filepath` param `str`** (the §B fix) so an inode-returning
   observer is usable through the API — enabling the hard-link shared-inode capstone
   (`stat(a) == stat(b)` after `link(a, b)`).

When (1) lands, the seven consequence postconditions in `formal_os_namespace.py` flip
from Unknown to Valid with NO change to the test (the test already asserts the true
consequence). That is the convergence fixed point for the namespace.

## Probes kept (the honest test itself is the reproducer)

`pure_lib_test/formal_os_namespace.py` — API-only, simulation-free (grep confirms NO
`disk`/`_dir_lookup`/`sys_`/`UnixInodeFileSystem`/`_filesystem` in any code line). It
emits cleanly; the seven consequence postconditions are Unknown as tabulated above. It
is left in place, clearly commented, as the standing reproducer for this gap (per the
loop rule: keep the honest API-calling test even when it does not prove).
