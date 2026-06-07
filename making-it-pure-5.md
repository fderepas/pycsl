# Making It Pure (v5): A Confined Pure-Python World

The definitive plan for pure-Python models of every stdlib module in `lib/calling.json`.
Synthesizes v1's per-module designs, v2's shared-World architecture, v3's Unix-skill grounding,
v4's frame-probe gate, and the v4 review's resolution of the framing problem via **HAPPY
confinement**.

**What changed in v5 (the framing breakthrough):**
1. **Preservation/coherence is now achieved by confinement, not per-call `assigns`.** A new §2
   declares one **HAPPY** integrity property per World subsystem ("only fs methods write
   `world.fs.*`", etc.). HAPPY expands to a per-write `#@ check` at every write site, so
   cross-subsystem preservation falls out as a corollary of a global invariant — with **0 new IR
   nodes, 0 backend change, 0 `\trusted`**, and *no* call-graph or alias analysis.
2. **§6 is de-risked.** The make-or-break question is no longer "can the memory model express sound
   component-level `assigns`?" (a property we don't control) but "can a HAPPY expand to per-site
   `#@ check`s Why3 discharges?" — almost certainly yes, by the `act` / `region_integrity`
   precedent.
3. **§9 splits into a coarse and a fine probe.** The coarse case (cross-subsystem) is handled by
   Tier-1 HAPPY and should pass trivially; the entire residual risk collapses onto the fine case
   (intra-subsystem, same fs region), addressed by **parametric HAPPY** (new §10) or, as a fallback,
   a narrow inode-granular `assigns` confined to a tiny audited core.
4. Honest scope: HAPPY buys **integrity** (preservation/coherence), not **values** — functional
   "what does read return after write" stays an ordinary `ensures`.

---

## 1. The World: a pure-Python kernel

The Unix kernel maintains **one** coherent state — one filesystem, one process table, one clock.
The models compose over a single shared `World` **by reference** (private copies would let you prove
false cross-module theorems). The key v5 insight: the World is **region-partitioned by ownership**,
exactly as the Unix on-disk layout is (superblock | inode table | data | bitmaps, skill §3), and
**confinement (§2) — not per-call framing — keeps it coherent.**

### 1.1 What the kernel holds (Unix skill §1–§12)

| Subsystem | State | Owner methods (the `except` set in §2) |
|---|---|---|
| Filesystem (§3–§5) | superblock, inodes, data blocks, free bitmaps, dir entries | fs methods |
| FD table (§5.1) | per-process FD→(open-file-description, offset, flags) | fs methods |
| Process table / env (§6, §7.2) | pid, creds, cwd, env, umask, argv | proc methods |
| Clock (§8.4) | monotonic counter | `ClockModel.monotonic` |
| Pipes (§5.7) | unidirectional byte buffers | subprocess/fs pipe methods |

### 1.2 The World class

```python
class World:
    """Single mutable state — one fs, one proc table, one clock. Region-partitioned (see §2)."""
    def __init__(self):
        self.clock = ClockModel()
        self.fs = UnixInodeFileSystem(clock=self.clock)
        self.proc = ProcessState(fs=self.fs, clock=self.clock)
```

### 1.3 ProcessState (Unix §6.1, §7.2) — owns `world.proc.*`

```python
class ProcessState:
    def __init__(self, fs, clock):
        self.pid = 1; self.ppid = 0; self.uid = 0; self.gid = 0
        self.umask = 0o022
        self.cwd_inode = 0           # root inode
        self.argv = []; self.environ = []; self.path = []
        self.exit_code = -1
        self.fs = fs                 # shared reference (FDs 0,1,2 live in fs's fd_table)
        self.clock = clock           # shared reference
```

§5.1: "`fork()` copies descriptor-table entries that still refer to the same open file
descriptions." stdin/stdout/stderr are fds into the *shared* fd table, never private buffers.

### 1.4 ClockModel (Unix §8.4: "`CLOCK_MONOTONIC` never goes backward") — owns `world.clock._ticks`

```python
class ClockModel:
    #@ class invariant self._ticks >= 0
    def __init__(self):
        self._ticks = 0
    #@ ensures \result >= 0
    #@ ensures self._ticks >= \result
    def monotonic(self) -> int:
        self._ticks = self._ticks + 1
        return self._ticks
```

Models a strictly-increasing tick — *one* legal monotonic behaviour (ordering only; not rate,
duration, or the real clock's equal successive reads). Body and contract agree
(`\result == \old(_ticks)+1`).

### 1.5 UnixInodeFileSystem — owns `world.fs.*`

Already models inodes (§3.3), data blocks (§3.1), free bitmaps (§3.5), directory entries (§3.4),
the FD table (§5.1), permissions (§4.3). v3/v4 amendments: accept a `ClockModel` for mtime (§4.1);
expose the fd_table so `sys`/`io`/`subprocess` share FD state (§5.1).

---

## 2. Confinement via HAPPY (the coherence mechanism)

A **HAPPY** (High-level Assertion-Producing PYthon requirement) declares one whole-program
integrity property over a shared field and **expands** it into a per-write `#@ check` at every
write site in every method outside its `except` set. It is PyCSL's analogue of MetAcsl's HILARE,
and adds **0 IR nodes, 0 backend change, 0 `\trusted`**. Two properties make it sound with no
alias/call-graph analysis: **universal per-site coverage** (an indirect write through a callee is
caught at the callee's own site) and a **trust boundary** (a `\trusted` mutator opts in with
`#@ \preserves`; a non-exempt bodyless mutator without it is a hard error).

### 2.1 Tier 1 — ownership HAPPYs (all cross-subsystem framing)

Declare one confinement property per subsystem field. Each says "no method outside the owner set
writes this field," which expands to a forbidding `#@ check` at any stray write site:

```python
#@ happy fs_ownership:
#@     protects world.fs.disk, world.fs.inodes, world.fs.bitmaps, world.fs.fd_table
#@     writes outside owner set forbidden
#@     except <fs methods: sys_open, sys_write, _write_inode, _write_directory, _alloc, ...>

#@ happy proc_ownership:
#@     protects world.proc.cwd_inode, world.proc.environ, world.proc.argv, world.proc.umask, ...
#@     writes outside owner set forbidden
#@     except <proc methods: chdir, setenv, umask_set, ...>

#@ happy clock_ownership:
#@     protects world.clock._ticks
#@     writes outside owner set forbidden
#@     except monotonic
```

Plus the existing intra-fs region property, unchanged:

```python
#@ happy region_integrity:
#@     region 512 .. 2560
#@     writes self.disk outside region
#@     except _write_inode, _write_directory
```

**What this buys, for free:** because `sys`, `io`, `time`, `subprocess`, and the pure modules have
**no direct write sites** into `world.fs.*` (all their fs mutation routes through fs methods — e.g.
`io.StreamModel.write` calls `world.fs.sys_write`), the per-site checks confirm they cannot perturb
the fs region. Therefore **any fs file is preserved across a `sys`/`time`/`io` call with no
`assigns` clause at all** — preservation is a corollary of the ownership invariant, not a per-call
frame obligation. This is the bulk of the plan's "cross-module" interactions, made sound by
confinement.

### 2.2 The trust boundary maps onto the syscall stubs

Every `\trusted` low-level mutator (the bodyless syscall stubs) carries `#@ \preserves` for the
regions it must not violate; the HAPPY composition theorem then holds across verified *and* trusted
code. A non-exempt bodyless mutator missing `\preserves` is the hard error HAPPY already specifies —
this is exactly the discipline the resource tier needs.

### 2.3 Honest limit — HAPPY frames integrity, not values, and not intra-subsystem objects

- **Values are still ordinary `ensures`.** "What does `os.read` return after `os.write`" is a
  functional postcondition; HAPPY says nothing about it. HAPPY buys *preservation* (B is untouched),
  not *behaviour* (what A now contains).
- **Intra-subsystem per-object preservation is out of Tier 1.** When A and B are *both* fs inodes
  and `mkstemp` legitimately writes the fs region, ownership confinement only says "mkstemp may write
  fs," not "mkstemp left B's inode alone." A fixed numeric region cannot express "only the inode for
  *this* file." This residual case is Tier 2 (§10) and the §9 *fine* probe.

### 2.4 Surface extension required

HAPPY as documented targets `self.<field>`; the World needs it over a **nested shared** field
(`world.fs.disk`). This is a modest reachability extension to the expansion's write-site matcher, not
a new mechanism.

---

## 3. Three buckets: modelled / specified / stubbed

| Bucket | Meaning | VC value |
|---|---|---|
| **Modelled** | pure-Python stand-in preserving real semantics | a real proof |
| **Specified** | axiomatized contract you trust (enters the TCB) | sound only for stated properties |
| **Stubbed** | signature only | proves nothing |

Coverage is always reported per bucket. A 100%-specified module can show "100% proven" and
guarantee nothing.

---

## 4. Module-by-module plan

(Bucketing unchanged from v4; the framing column now reads "confined by §2 ownership HAPPY" instead
of per-call `assigns`.)

- **`time`** (1) — `monotonic` **Modelled**; owns `clock._ticks` (clock_ownership). Build first.
- **`sys`** (10) — all **Modelled** façade over `world.proc` + shared fd table; **no fs write
  sites** → fs preserved by confinement. No new class.
- **`io`** (4) — `open`/`StringIO` **Modelled**, `TextIOWrapper`/`text_encoding` **Specified**.
  `StreamModel` uses **flush-through** (§8): `write` routes to `world.fs.sys_write`, so the *only*
  fs write site is inside fs (covered by fs_ownership at the callee site — HAPPY's per-site coverage
  in action).
- **`subprocess`** (93; ~5 core) — `Popen`/`poll`/`wait`/`list2cmdline`/classes **Modelled**;
  `run`/`communicate` **Modelled plumbing / output Specified** (output is whatever the stubbed child
  wrote); child execution **Stubbed**. Pipes are `list[int]` (§5.7).
- **`tempfile`** (26) — over fs, **Modelled**; `_RandomNameSequence` **Specified** (counter; TCB:
  collision-freedom not modelled).
- **`shutil`** (47) — compositions of `os` over `world.fs`, **Modelled**. Cross-module
  postcondition: after `copyfile(src,dst)`, *contents* equal — `sys_read(dst,n)==sys_read(src,n)` —
  **provable given the copy-loop invariant**; `copy2`/`copystat` then mutate dst timestamps, so
  inodes diverge at the metadata level (content equality only).
- **`hashlib`** (1) — `sha256` **Specified** (uninterpreted value; only length contracts modelled).
- **quick wins** — `__future__`/`keyword`/`bisect`/`enum`/`collections` **Modelled** (no World);
  `unicodedata` **Specified**.
- **`ast`** (8) — `parse` **Stubbed**; `dump` recursion **Modelled** / string formatting **Specified
  (string-heavy)**.
- **`contextlib`** (9) — `ExitStack`/`nullcontext` **Modelled**; `contextmanager` **Specified**.
- **`copy`** (15) — `deepcopy` **Modelled-hard** (sharing/cycle aliasing); defer (same dependency as
  §10).
- **`inspect`** (12) — `unwrap` **Modelled**; `cleandoc` **Specified (string-heavy)**; `signature`
  **Stubbed**.
- **`sysconfig`** (41) — dict ops **Modelled**; `_subst_vars` **Specified (string-heavy)**.
- **`typing`** (52) — `cast` **Modelled but proves nothing useful**; rest **Stubbed**.
- **`tokenize`** (21) — core **Specified (string-heavy)**; constants **Modelled**.
- **`pathlib`** (65) — path parse **Specified (string-heavy)**; fs methods **Modelled** via `world.fs`.
- **`dataclasses`** (60) — `field`/`fields` **Modelled**; `@dataclass` (`exec`) **Stubbed**.
- **`argparse`** (66) — state **Modelled**; `parse_args` **Specified (string-heavy)**; help **Stubbed**.

---

## 5. Soundness Ledger (TCB)

| Where | Real property deleted/axiomatized | Consequence |
|---|---|---|
| `hashlib` | hash value / collision resistance | value-dependent VCs prove nothing |
| `unicodedata` | Unicode database | name/normalization assumed |
| `ast.parse` | parsing semantics | downstream untyped |
| `subprocess` child + `run`/`communicate` output | program execution | plumbing + returncode only; outputs specified |
| `tempfile` names | unpredictability / collision-freedom | racy code can verify |
| `time` rate | wall-clock duration | ordering only |
| string-heavy paths (`io` text, `pathlib`, `tokenize`, `argparse`, `inspect`, `sysconfig`, `ast.dump`) | encoding / string processing | specified/stubbed |
| `typing` | type introspection | `cast` proves nothing |
| `dataclasses` | dynamic class construction | generative core unverified |
| **HAPPY `\preserves` on `\trusted` stubs** | the stub actually preserves its declared regions | confinement theorem trusts these assumptions |

The last row is new: the HAPPY trust boundary is itself a (small, explicit, auditable) TCB entry. A
`--soundness-report` (§6 Q4) should surface all rows, including which VCs rest on `\preserves`.

---

## 6. Open questions — with honest answers

1. **Can the framing strategy work?** **Yes, with high confidence, and it no longer hinges on the
   memory model.** v5 replaces per-call `assigns world.fs.…` with HAPPY confinement (§2), whose
   soundness rests on per-site `#@ check` coverage — the same expansion the `act` and
   `region_integrity` precedents already discharge with 0 backend change. The only genuinely open
   piece is the *intra-subsystem* fine case (Q2).

2. **The residual hard case — A written, B preserved, both in the fs region.** Tier-1 ownership
   confinement does not cover this (mkstemp legitimately writes fs). Two scoped options, decided by
   the §9 *fine* probe: (a) **parametric HAPPY** (§10) — confine by a per-call footprint argument
   (`written_inode == n`), still pure `#@ check` expansion; or (b) **fallback** — a narrow
   `assigns world.fs.inodes[n]` only at the inode-granular leaf ops, with Tier-1 HAPPY handling
   everything above, so heavyweight framing lives in a tiny audited core.

3. **Stream aliasing.** Answered: §8 flush-through, which *composes* with §2 (io has no direct fs
   write site; the write lands in `fs.sys_write`, covered by `fs_ownership`).

4. **TCB growth.** The Soundness Ledger now includes the HAPPY `\preserves` assumptions. A
   `--soundness-report` must distinguish Modelled VCs from those resting on Specified/Stubbed/
   `\preserves`.

5. **Coverage honesty.** Reported per bucket.

---

## 7. Relationship to existing code

| File | Status | v5 impact |
|---|---|---|
| `pure_lib/os/UnixInodeFileSystem.py` | 98.0% proven (audit: Modelled-bucket?) | accept ClockModel; expose fd_table; add to `fs_ownership` except set |
| `pure_lib/os/__init__.py` | Done | no change |
| `pure_lib/re/_engine.py` | 16/16 formal VCs | no World dependency |
| `pure_lib/warn/__init__.py` | 18/18 body VCs | no World dependency |
| `pure_lib/json/_api.py` | 6/6 formal VCs | no World dependency |
| HAPPY expansion (front end) | `region_integrity` precedent exists | extend write-site matcher to nested shared fields (§2.4) |

---

## 8. Implementation order

| Phase | Step | Notes |
|---|---|---|
| **1. Foundation** | `time` → ClockModel; wire fs↔clock; `World` aggregate | clock first |
| **2. Confinement** | declare Tier-1 ownership HAPPYs (§2.1); extend HAPPY matcher to nested fields (§2.4); add `\preserves` to `\trusted` stubs | the coherence mechanism |
| **3. Quick wins** | `bisect`,`keyword`,`enum`,`__future__`,`collections`,`unicodedata` | no World |
| **3.5 Coarse probe** | §9 coarse | should pass via Tier-1 HAPPY |
| **3.6 Fine probe (gate)** | §9 fine | **decides Tier-2 path (Q2a vs Q2b) before fs-mutating modules** |
| **4. Façades** | `sys`, `io` (flush-through §8) | no direct fs writes |
| **5. Filesystem** | `tempfile`, `shutil` | use the Tier-2 mechanism chosen at 3.6 |
| **6. Stubs** | `hashlib`,`ast`,`contextlib`,`inspect` | specified/mixed |
| **7. Hard** | `copy` (aliasing), `subprocess` | |
| **8. String-heavy** | `sysconfig`,`typing`,`tokenize`,`pathlib`,`dataclasses`,`argparse` | mostly specified/stubbed |

The gate moved earlier and split: the *coarse* probe validates the HAPPY confinement idea cheaply;
the *fine* probe is the only remaining go/no-go, and it chooses between parametric HAPPY and the
narrow-`assigns` fallback before any fs-mutating module is built.

---

## 9. Appendix: the frame probes (split)

Build only `time`, the clock-wired `UnixInodeFileSystem`, the `World`, and the Tier-1 HAPPYs.
Pre-create two files A and B.

**Coarse probe (cross-subsystem — Tier-1 HAPPY).** Call a `sys`/`time` operation; prove an fs file
is preserved with **no `assigns`**:
```python
#@ ensures sys_stat(ino_A) == \old(sys_stat(ino_A))   # fs preserved across a proc/clock call
def coarse(world, ino_A): world.proc... ; world.clock.monotonic()
```
*Pass:* discharges from the `fs_ownership` HAPPY alone (the call has no fs write site). Expected to
pass trivially — this validates the whole confinement approach.

**Fine probe (intra-subsystem — the real gate).** `mkstemp` writes A; prove B (another fs inode) is
preserved:
```python
#@ assigns world.fs.inodes[ino_A], world.fs.disk        # or: parametric-HAPPY footprint
#@ ensures sys_read(fd_A, n) == data                    # (1) read-after-write on A
#@ ensures sys_stat(ino_B) == \old(sys_stat(ino_B))     # (2) B preserved
def fine(world, fd_A, data, ino_B): ...
```
*Pass criteria (both):* (1) read-after-write on A discharges, and (2) B is preserved **without
naming B in the footprint**. *If (2) needs the whole fs region:* parametric HAPPY (§10) is required;
if even that cannot express per-inode confinement, fall back to narrow inode `assigns` confined to
leaf ops. *Outcome decides Phase 5's mechanism.*

---

## 10. Appendix: parametric HAPPY (Tier-2 sub-proposal)

Extend the HAPPY region predicate to be **parameterized by a method's footprint argument**, so
per-object (not just fixed-region) confinement stays pure `#@ check` expansion:

```python
#@ happy inode_confinement(n):
#@     a method declaring footprint inode n
#@     may write only world.fs.inodes[n] (+ allocator regions)
#@     expands to per-site:  #@ check written_inode == n
```

A method annotates the inode it operates on; the injected per-site check becomes
`written_inode == n`. This generalizes fixed-region confinement (`i < 512 or i >= 2560`) to
per-object confinement while preserving the per-site-coverage soundness theorem and adding **0
backend change** (still expansion onto `#@ check`). It is a real but natural front-end feature, and
it is the preferred answer to §6 Q2 / the §9 fine probe. The narrow-`assigns` fallback is the
contingency if parametric HAPPY proves too costly to land in this cycle.

**Honest scope (same as §2.3):** parametric HAPPY confines *which* object is written, not *what
value* it holds — functional behaviour remains ordinary `ensures`.
