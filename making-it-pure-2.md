# Making It Pure (v2): Abstract Models over a Shared World

This is the synthesis of the original *Making It Pure* plan, the design review of it, and the
shared-state observation that the abstract models cannot be independent. The **method** —
modelling an environment as a Python data structure, as `UnixInodeFileSystem` does for the Unix
inode layer — is sound and unchanged. v2 adds three things the first draft lacked:

1. **A shared `World`** so that every model touching the same resource (files, processes, time,
   streams) operates on *one* mutable state by reference — never a private copy. This is required
   for **coherence and soundness**, not polish.
2. **A modelled / specified / stubbed classification** for every symbol, because "proven VC" means
   completely different things in each bucket.
3. **An explicit soundness ledger** recording every place a model deletes a real property (and
   therefore enlarges the trusted base), plus corrected contracts and re-baselined coverage.

---

## Principle A — Three buckets, not one

Every symbol falls into exactly one of:

- **Modelled** — a data stand-in that *preserves the real semantics* (inodes as arrays). A proof
  here is a real proof of the real behaviour.
- **Specified** — the real semantics are replaced by an *axiomatized contract you now trust*
  (the SHA-256 value, Unicode tables). A "proof" here is sound only for the properties the
  contract states; the underlying behaviour is in the **TCB**.
- **Stubbed** — only a signature, no semantics (`ast.parse`). Proves nothing about the symbol.

A module that is 100% specified/stubbed can report "100% of VCs proven" while guaranteeing nothing.
Coverage must always be reported per bucket (see the Coverage Ledger). The headline
"`os`: 98% of 4101 VCs proven" is the argument for this whole approach and must be audited to
confirm those are **modelled-bucket** VCs, not specified/stubbed ones.

## Principle B — One World, shared by reference

A real operating system has *one* kernel state; `os`, `sys`, `io`, `subprocess`, `tempfile`, and
`shutil` are libraries that all call into it. The models must mirror that. Any model that touches
files, processes, time, or streams composes over a single shared aggregate and **never owns a
private copy of shared state**:

```
World
├── clock : ClockModel             # monotonic ticks
├── fs    : UnixInodeFileSystem     # inodes, data blocks, free bitmap, directories
│     └── (reads clock for inode timestamps, when timestamps are modelled)
└── proc  : ProcessTable
      └── current process:
            cwd      : inode number
            env      : list of byte-array pairs
            argv     : list of byte arrays
            umask    : int
            pid      : int
            fd_table : list of open-file descriptors  # [inode_or_pipe, offset, flags]
```

**The coherence guarantee this buys:** a file created through `tempfile.mkstemp` is the *same*
inode that `os.stat` observes, that `io.open` reads, that `shutil.copyfile` duplicates, that a
`subprocess` child inherits, and whose mtime is stamped by the *same* `time` clock. Cross-module
postconditions (`after copyfile, os.read(dst) == os.read(src)`) become both *statable* and
*sound*. With private copies they are neither.

**The links that must exist (the user's point, made systematic):**

| Model | Shares, by reference | Why |
|---|---|---|
| `sys` | `proc` (argv, path, env, exit, umask); `fd_table` for stdin/stdout/stderr | std streams *are* fds 0/1/2 into the fs or pipes; `sys` is a façade over process state, not an owner |
| `io` | `fs` + an `fd` | `io.open` returns a stream **backed by** an inode; the stream operates *through* its fd (see aliasing caveat) |
| `tempfile` | `fs` (+ a world-level name counter) | temp files are ordinary inodes in a designated directory |
| `shutil` | `fs` | high-level composition of `os` primitives on the one fs |
| `subprocess` | `fs` (child reads/writes files), `proc` (cwd/env inherited), pipes connect parent/child fds | a child shares the filesystem and inherits process state |
| `os` | `fs` + `proc` | the fs itself plus cwd/env/pid/umask/fd_table |
| `time` | (provider) consumed by `fs` for timestamps | inode mtime/atime/ctime read the shared clock |
| `hashlib` | nothing | consumes a byte list; holds no world state |

**The cost, stated honestly.** Sharing mutable state introduces **aliasing and frame reasoning** —
exactly the hard part for the memory model. `assigns` clauses now name sub-parts of the World
(`assigns world.fs.inodes[dst]`), and a stream that buffers must model the buffer↔inode flush
relationship or its writes become invisible to a concurrent `os.read` on the same fd (an
unsoundness). So the shared World is **necessary for sound cross-module proofs but raises
verification difficulty**; you cannot have cheap independent models *and* coherent proofs. PyCSL's
memory model (`typed`/`store`) must carry references into the shared World for this to work; the
`hoare` model likely cannot express the aliasing and is unsuitable for the resource-touching tier.

---

## Precedent: `UnixInodeFileSystem` (modelled) ✅

Models inodes (fixed-size arrays), data blocks (flat byte array), the free bitmap, file
descriptors, and directory entries; every `os` function manipulates these with pure integer
arithmetic. **v2 amendment:** the fs takes a `ClockModel` reference so `open`/`write`/`mkdir` stamp
inode mtime from the shared clock (omit the link only if timestamps are deliberately not modelled —
but then `copy2`/`copystat` cannot claim to copy them).

---

## Tier 1 — Models over the World

### `sys` → façade over `proc` (10 symbols)
**Links:** reads/writes `world.proc` (argv, path, env, umask, exit code); stdin/stdout/stderr are
fds in `fd_table`. **Not** an owner of stream state.
- **Modelled:** `argv`, `path`, `path.insert`, `exit`, `float_info.max_10_exp` (constant), umask.
- **Specified/Stubbed:** none essential.
**Caveat:** `stdin/stdout/stderr` only behave correctly if routed through the shared `fd_table`;
a private `_stdin_buffer` would desync from any `os`/`io` view of the same fd.

### `io` → `StreamModel` over `fs` + fd (4 symbols)
**Links:** `open` delegates to `world.fs.open`; the `StreamModel` operates *through* its fd.
- **Modelled:** `StringIO` (in-memory buffer), buffer position/offset arithmetic, `open` plumbing.
- **Specified/Stubbed:** text encoding/decoding (`TextIOWrapper`, `text_encoding`) — string-heavy,
  axiomatized.
**Caveat (aliasing):** a buffered stream must model flush-to-inode, or writes are lost relative to
`os.read`. State the buffering model explicitly; do not let the stream hold a divergent copy.

### `subprocess` → `ProcessModel` + `ProcessTable` over the World (93 symbols, ~5 core)
**Links:** child shares `world.fs`; inherits `cwd`/`env` from `world.proc`; pipes are byte buffers
joining parent/child fds.
- **Modelled:** pipe plumbing (bytes in/out), `poll`/`wait`/`communicate` state machine,
  `list2cmdline` (string join), `returncode` bookkeeping; exception classes.
- **Specified/Stubbed:** **the child's actual execution.** "A child process is a state machine with
  pipes" means *every property about what the program does* is unmodelled.
**Caveat (loud):** proofs cover the plumbing, never the child's behaviour — this is the `hashlib`
problem at module scale. POSIX only; Windows branches dropped.

### `tempfile` → over `fs` (26 symbols)
**Links:** `mkstemp` calls `world.fs.open` in the temp dir; name counter is world-level.
- **Modelled:** file creation, `gettempdir`, wrapper close→unlink.
- **Specified:** **name unpredictability replaced by a counter.**
**Caveat (loud):** `mkstemp`'s purpose is a collision-free, unpredictable name. A deterministic
counter cannot exhibit the collision/race the real function is designed to avoid, so proofs do
**not** cover the security/uniqueness property anyone actually wants from `tempfile`.

### `shutil` → over `fs` (47 symbols)
**Links:** operates directly on `world.fs`. No new model.
- **Modelled:** `copyfile`, `copyfileobj`, `copystat`, `copy2`, `rmtree` (needs loop invariants),
  `which` (PATH search — string-heavy, partly specified).
**Caveat:** each is a composition of already-proven `os` primitives; the only real difficulty is
recursive traversal (`rmtree`).

### `time` → `ClockModel` (1 symbol)
**Links:** consumed by `fs` for timestamps; foundational (build first).
- **Modelled:** `monotonic` over a tick counter.
**Corrected contract (v1 was wrong):** monotonic is **non-decreasing**, and a return-then-increment
body returns the *old* value. Use:
```
#@ ensures \result >= \old(_ticks)
#@ ensures _ticks >= \result
def monotonic(self) -> int:
    self._ticks = self._ticks + 1
    return self._ticks            # or: r = _ticks; return r  — but keep ensures consistent
```
**Caveat:** real `monotonic` is nondeterministic in *rate*; a counter models ordering only, not
durations. Proofs about elapsed real time do not transfer.

### `hashlib` → `HashModel` (1 symbol)
**Links:** none (consumes a byte list).
- **Specified:** the digest **value** is an uninterpreted function (axiom: equal input → equal
  output). Only `\length(digest)==32`, `\length(hexdigest)==64`, and determinism are claimed.
**Caveat (loud):** any VC depending on the *actual* hash value (collision resistance, a specific
digest of specific bytes) proves nothing — the hash is in the TCB.

---

## Tier 2 — Pure logic (mostly independent of the World)

Tagged with the realistic modelled-vs-stub split, since symbol counts overstate value.

| Module | Sym | Verdict |
|---|---|---|
| `__future__` | 2 | **Modelled** (constants). Trivial. |
| `keyword` | 1 | **Modelled** (constant list). Trivial. |
| `bisect` | 2 | **Modelled** — classic integer binary search, body-provable. Best ROI. |
| `enum` | 2 | **Modelled** — int class + auto counter. |
| `collections` | 2 | **Modelled** — array-backed `deque`, `defaultdict`. Integer indices. |
| `unicodedata` | 2 | **Specified** — Unicode DB axiomatized (name→char, normalize idempotence). |
| `ast` | 8 | `dump` **Modelled** (recursive string build); `parse` **Stubbed** (CPython C API). |
| `contextlib` | 9 | `ExitStack`/`nullcontext` **Modelled**; `@contextmanager` (generators) **mostly Stubbed**. |
| `inspect` | 12 | `unwrap` **Modelled** (loop); `cleandoc` string-heavy **Specified**; `signature` **Stubbed**. |
| `copy` | 15 | **Modelled but hard** — `deepcopy` over arbitrary graphs needs sharing/cycle (aliasing) reasoning; *not* pure logic. Interacts with the memory model. |
| `sysconfig` | 41 | config **dict** **Modelled**; `_subst_vars` string-formatting **Specified**. |
| `typing` | 52 | mostly **Stubbed/identity** (`cast` = `return val` — verifies *nothing useful*); a few dict lookups Modelled. |
| `tokenize` | 21 | character state machine, string-heavy → **mostly Stubbed** for body verification. |
| `pathlib` | 65 | path parse/join **Modelled** (string); filesystem methods delegate to **World** `fs`; high symbol count is **thin wrappers**, real coverage low. |
| `dataclasses` | 60 | `field`/`fields` **Modelled**; the `@dataclass` decorator (`exec`/`type`) **Stubbed** — i.e. the whole point is unverifiable. |

---

## Tier 3 — Thin API wrapper pattern

For `argparse` (66), `subprocess` (93), `pathlib` (65), `dataclasses` (60), `typing` (52): use the
`json/_api.py` pattern — body-verified functions for integer/boolean-heavy logic, **stub wrappers**
(declared as such) for the rest. Report the body-verified fraction; do not let the symbol count
imply coverage.

---

## Soundness Ledger (what you are trusting)

Every entry here is added to the **TCB** by a specified/stubbed choice. This table is the honest
answer to "what does a green run *not* guarantee?"

| Where | Real property deleted / axiomatized | Consequence |
|---|---|---|
| `hashlib` | the hash value / collision resistance | value-dependent VCs prove nothing |
| `unicodedata` | the Unicode database | name/normalization facts are assumed |
| `ast.parse` | parsing semantics | downstream of `parse` is untyped/unmodelled |
| `subprocess` child | program execution | only pipe plumbing is covered |
| `tempfile` names | unpredictability / collision-freedom | racy/insecure code can verify |
| `time` | rate / wall-clock duration | only ordering is modelled |
| `io`/`inspect`/`sysconfig`/`tokenize` text | encoding/decoding, string processing | string-heavy paths are stubs |
| `dataclasses`/`argparse` decorators | dynamic class/parser construction | the generative core is unverified |

---

## Coverage Ledger (re-baselined)

| Module | Abstract model | Shares World? | Dominant bucket |
|---|---|---|---|
| `os` ✅ | `UnixInodeFileSystem` (+clock) | is the fs | **Modelled** (audit the 98%) |
| `time` | `ClockModel` | provides clock | **Modelled** (build first) |
| `sys` | façade | `proc`, `fd_table` | **Modelled** |
| `io` | `StreamModel` | `fs` + fd | Modelled buffer / **Specified** text |
| `tempfile` | over fs | `fs` | Modelled / **Specified** names |
| `shutil` | over fs | `fs` | **Modelled** |
| `hashlib` | `HashModel` | no | **Specified** |
| `subprocess` | `ProcessModel`+`ProcessTable` | `fs`,`proc`,pipes | Modelled plumbing / **Specified** execution |
| `bisect`,`enum`,`collections`,`keyword`,`__future__` | none | no | **Modelled** |
| `copy` | none | no (but aliasing) | **Modelled-hard** |
| `pathlib`,`typing`,`dataclasses`,`argparse`,`tokenize` | thin wrapper | `fs` (pathlib only) | **mostly Stubbed** |

---

## Implementation order (revised, World-aware)

Foundations first (everything depends on them), then independent integer-heavy wins, then façades,
then the aliasing- and string-heavy hard cases.

1. **`time` → `ClockModel`** — foundational; the fs timestamps depend on it.
2. **Audit & wire the fs↔clock link** in `UnixInodeFileSystem`; confirm the 98% is modelled-bucket.
3. **`World` aggregate** — define `{clock, fs, proc}` and the reference discipline; pick the memory
   model (`typed`/`store`) that can carry World references. *This is the gating architectural step.*
4. **Independent pure wins:** `bisect`, `keyword`, `enum`, `collections`, `__future__`.
5. **`sys`** façade over `proc`/`fd_table`.
6. **`io` `StreamModel`** over fs+fd, with an explicit buffer↔inode flush model.
7. **`tempfile`**, then **`shutil`** — over the shared fs.
8. **Specified/stub modules** with loud caveats: `hashlib`, `unicodedata`, `ast`.
9. **Aliasing-hard:** `copy.deepcopy` (only once the memory model supports sharing/cycles).
10. **String-heavy / thin-wrapper:** `sysconfig`, `typing`, `tokenize`, `pathlib`, `dataclasses`,
    `argparse`, `subprocess` — body-verify the integer core, declare the rest stubbed.

---

## Open questions / risks

1. **Memory-model fit.** Does PyCSL's `typed`/`store` model express references into a shared mutable
   `World` with sound `assigns`? If not, the resource-touching tier cannot be modelled coherently —
   this is the make-or-break question and should be answered before step 3.
2. **Frame-condition scale.** As `assigns` clauses name World sub-parts, do they stay tractable, or
   does every cross-module call drag in the whole World?
3. **Stream aliasing.** What is the canonical buffer↔inode model so `io` writes and `os` reads on the
   same fd stay consistent without unsoundness?
4. **TCB growth.** The Soundness Ledger is the new trusted surface. Is each entry acceptable, and is
   it surfaced to users (a `--soundness-report` listing which proven VCs rest on specified/stubbed
   models)?
5. **Coverage honesty.** Will the public coverage number be reported per bucket, so "proven" cannot
   be mistaken for "modelled"?
