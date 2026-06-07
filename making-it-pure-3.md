# Making It Pure (v3): From Unix Kernel to Pure-Python World

This is the definitive plan for creating pure-Python models of every
stdlib module in `lib/calling.json`. It synthesizes:
- v1's concrete model designs per module
- v2's shared-World architecture and three-bucket classification
- The `config/skills/unix/` skill (Unix kernel internals, syscall
  semantics, data structures, algorithms)

The key insight from the Unix skill: the kernel maintains **one**
coherent state — one filesystem, one process table, one clock. Our
models must mirror that. Independent per-module models would be like
having two different kernels — incoherent and unsound for cross-module
proofs.

---

## 1. The World: a pure-Python kernel

### 1.1 What the real kernel holds

From the Unix skill (§1–§12):

| Kernel subsystem | State | Syscalls that touch it |
|---|---|---|
| Filesystem (§3–§5) | Superblock, inode table, data blocks, free bitmaps, directory entries | open, read, write, close, stat, link, unlink, mkdir, rename |
| File descriptor table (§5.1) | Per-process FD→(open-file-description, offset, flags) | open, close, read, write, dup, dup2, fcntl, pipe |
| Process table (§6) | PID, state, credentials, parent, children, signal dispositions | fork, execve, _exit, wait, kill, getpid |
| Process environment (§7.2) | argv, envp, cwd, umask | execve, chdir, umask |
| Clock/timekeeping (§8.4) | Monotonic counter, wall clock | clock_gettime, times, alarm |
| Pipes (§5.7) | Unidirectional byte buffers connecting two FDs | pipe, read, write |
| Signals (§7.5) | Pending mask, dispositions, blocked mask | sigaction, sigprocmask, kill |

### 1.2 The World class

```python
class World:
    """The single mutable state shared by all stdlib models.

    Mirrors the Unix kernel's coherent view: one filesystem,
    one process table, one clock. Every module that touches
    external state receives a reference to this World.
    """
    def __init__(self):
        self.clock = ClockModel()
        self.fs = UnixInodeFileSystem(clock=self.clock)
        self.proc = ProcessState(fs=self.fs, clock=self.clock)
```

### 1.3 ProcessState: what `sys` and `subprocess` read/write

From the Unix skill §6.1 (process control block) and §7.2 (execve):

```python
class ProcessState:
    """Per-process kernel state: credentials, environment, FDs."""
    def __init__(self, fs, clock):
        self.pid = 1
        self.ppid = 0
        self.uid = 0
        self.gid = 0
        self.umask = 0o022
        self.cwd_inode = 0          # root inode
        self.argv = []              # list of byte-arrays
        self.environ = []           # list of [key_bytes, val_bytes]
        self.path = []              # sys.path (module search)
        self.exit_code = -1         # -1 = still running
        # FDs 0,1,2 are stdin, stdout, stderr — they point into
        # the SAME fd_table as fs, not a private copy.
        # Reference: Unix skill §5.1
        self.fs = fs                # shared filesystem reference
        self.clock = clock          # shared clock reference
```

**Why not private copies?** Unix skill §5.1: "fork() copies descriptor-
table entries that still refer to the same open file descriptions."
A file opened via `tempfile.mkstemp()` is the *same* inode that
`os.stat()` observes, that `io.open()` reads, that `shutil.copyfile()`
duplicates. Private copies break this.

### 1.4 ClockModel

From the Unix skill §8.4: "`CLOCK_MONOTONIC` never goes backward."

```python
class ClockModel:
    """Monotonic clock: non-decreasing integer ticks."""
    #@ class invariant self._ticks >= 0
    def __init__(self):
        self._ticks = 0

    #@ ensures \result >= 0
    #@ ensures self._ticks >= \result
    def monotonic(self) -> int:
        self._ticks = self._ticks + 1
        return self._ticks
```

**What this models:** Ordering only. Not wall-clock time, not
durations, not rates. Proofs about "elapsed real time" do NOT transfer.

### 1.5 How UnixInodeFileSystem evolves

The existing `UnixInodeFileSystem` already models (Unix skill §3–§5):
- Inodes as 18-field arrays (§3.3: type, mode, uid, gid, size,
  link_count, direct blocks, timestamps)
- Data blocks as a flat byte array (§3.1: "array of logical blocks")
- Free bitmaps (§3.5: "block and inode bitmaps per block group")
- Directory entries as [inode_num, name_bytes] pairs (§3.4)
- FD table as parallel arrays: fd_open, fd_inode, fd_offset, fd_flags (§5.1)
- Permission checks with uid/gid/mode (§4.3)

**v3 amendments:**
1. Accept a `ClockModel` reference so `open`/`write`/`mkdir` stamp
   inode mtime from the shared clock (§4.1: "st_mtim: last data
   modification time")
2. Expose the fd_table so `sys`, `io`, and `subprocess` can reference
   the *same* FD state (§5.1: "entries point at open file descriptions")

---

## 2. Three buckets: modelled / specified / stubbed

From v2 Principle A. Every symbol falls into exactly one:

| Bucket | Meaning | VC value |
|---|---|---|
| **Modelled** | Pure-Python data stand-in preserving real semantics | A real proof |
| **Specified** | Axiomatized contract you trust (TCB) | Sound only for stated properties |
| **Stubbed** | Signature only, no semantics | Proves nothing about the symbol |

A module that is 100% specified/stubbed can report "100% of VCs proven"
while guaranteeing nothing. Coverage is always reported per bucket.

---

## 3. Module-by-module plan

### 3.1 `time` — ClockModel (1 symbol)

**Unix grounding:** §8.4 — `CLOCK_MONOTONIC` never goes backward.

| Symbol | Bucket | Implementation |
|---|---|---|
| `monotonic` | **Modelled** | `ClockModel.monotonic()` — increment-and-return |

**Build first.** The filesystem timestamps depend on it.

**Fields:** `_ticks: int` (≥0, non-decreasing).

**Contracts:**
- `ensures \result >= 0`
- `ensures self._ticks >= \result`

**TCB entry:** Rate and wall-clock duration are unmodelled.

---

### 3.2 `sys` — façade over ProcessState (10 symbols)

**Unix grounding:** §6.1 (process control block), §5.1 (fd table),
§7.2 (argv, envp).

| Symbol | Bucket | Implementation |
|---|---|---|
| `argv` | **Modelled** | `world.proc.argv` |
| `path` | **Modelled** | `world.proc.path` |
| `path.insert` | **Modelled** | list insert on `world.proc.path` |
| `exit` | **Modelled** | set `world.proc.exit_code`, raise SystemExit |
| `float_info` | **Modelled** | object with `max_10_exp = 308` (constant) |
| `float_info.max_10_exp` | **Modelled** | return 308 |
| `stdin` | **Modelled** | FD 0 in `world.fs.fd_*` tables |
| `stdin.buffer` | **Modelled** | raw byte view of FD 0 |
| `stdin.buffer.read` | **Modelled** | `world.fs.sys_read(0, n)` |
| `stderr` | **Modelled** | FD 2 in `world.fs.fd_*` tables |

**Key insight from Unix skill §5.1:** stdin/stdout/stderr are NOT
separate buffers — they are file descriptors 0, 1, 2 pointing into
the shared fd table. `sys.stdin.buffer.read()` is just `read(0, n)`.

**No new model class needed.** `sys` is a façade — it reads/writes
`ProcessState` and delegates I/O to the existing `UnixInodeFileSystem`.

---

### 3.3 `io` — StreamModel over fs+fd (4 symbols)

**Unix grounding:** §5.1 (file descriptors), §5.2 (open), §5.3
(read/write with short counts), §10.3 (terminal line discipline for
text mode).

| Symbol | Bucket | Implementation |
|---|---|---|
| `open` | **Modelled** | `world.fs.sys_open()` + wrap in StreamModel |
| `StringIO` | **Modelled** | In-memory buffer (list + position) |
| `TextIOWrapper` | **Specified** | Encoding/decoding axiomatized |
| `text_encoding` | **Specified** | Encoding normalization |

**StreamModel fields:**
```python
class StreamModel:
    _fd: int               # index into world.fs.fd_* tables
    _buffer: list[int]     # write-back buffer (flush → fd)
    _buf_pos: int          # position within buffer
    _mode: int             # 0=read, 1=write, 2=append
    _closed: int           # 0=open, 1=closed
```

**Aliasing caveat from v2:** A buffered stream must model flush-to-inode.
Without flush, writes through `io` are invisible to `os.read()` on the
same fd. The model either (a) flushes immediately (unbuffered — simpler,
sufficient for proof contracts), or (b) tracks dirty state. Option (a)
is recommended: it's sound and provable.

**StringIO** needs no fd — pure in-memory list with integer position.
Body-level provable (all integer arithmetic).

---

### 3.4 `subprocess` — ProcessModel + ProcessTable (93 symbols, ~5 core)

**Unix grounding:** §7.1 (fork), §7.2 (execve), §7.3 (_exit), §7.4
(wait), §5.7 (pipes for stdin/stdout/stderr redirection), §6.5 (parent-
child relationship).

| Core symbol | Bucket | Implementation |
|---|---|---|
| `Popen` | **Modelled** (plumbing) | Create ProcessModel, allocate pipes |
| `run` | **Modelled** (plumbing) | Popen + communicate + CompletedProcess |
| `communicate` | **Modelled** | Read stdout/stderr pipes, write stdin pipe |
| `poll` / `wait` | **Modelled** | Check/wait for returncode |
| `list2cmdline` | **Modelled** | Pure string join |
| `CompletedProcess` | **Modelled** | Data class (args, returncode, stdout, stderr) |
| `CalledProcessError` | **Modelled** | Exception class |
| `TimeoutExpired` | **Modelled** | Exception class |
| (child execution) | **Stubbed** | Unmodelled — "the child is a black box" |
| (93 internal symbols) | **Stubbed** | Platform-specific, winapi, threading |

**ProcessModel fields (from Unix skill §6.1, §5.7):**
```python
class ProcessModel:
    pid: int
    returncode: int         # -1 = running
    stdin_pipe: list[int]   # bytes parent writes to child
    stdout_pipe: list[int]  # bytes child produces
    stderr_pipe: list[int]  # bytes child produces
    args: list              # command + arguments
```

**ProcessTable fields (from Unix skill §6.2):**
```python
class ProcessTable:
    processes: list[ProcessModel]
    next_pid: int
    fs: UnixInodeFileSystem  # shared
```

**Pipes model (from Unix skill §5.7):** "pipe() creates a unidirectional
byte stream." Each pipe is a `list[int]` (byte buffer). Reading from
an empty pipe blocks (in the model: returns empty). Writing to a pipe
with no reader raises EPIPE. Writes up to `PIPE_BUF` are atomic.

**TCB entry:** The child's actual execution is unmodelled. Proofs
cover the plumbing (pipe I/O, returncode), never what the child does.

---

### 3.5 `tempfile` — over fs (26 symbols)

**Unix grounding:** §5.2 (open with O_CREAT|O_EXCL), §3.5 (free
block/inode allocation).

| Core symbol | Bucket | Implementation |
|---|---|---|
| `mkstemp` | **Modelled** | `world.fs.sys_open(name, O_CREAT\|O_EXCL)` in tempdir |
| `gettempdir` | **Modelled** | Return path to `_tempdir` inode |
| `NamedTemporaryFile` | **Modelled** | mkstemp + close→unlink wrapper |
| `_RandomNameSequence` | **Specified** | Counter replaces randomness |

**No separate model class.** Temp files are ordinary inodes in a
designated directory. The "randomness" in name generation is replaced
by a deterministic counter (specified: collision-freedom is unmodelled).

**TCB entry:** `mkstemp`'s purpose is unpredictable, collision-free
names. A deterministic counter cannot exhibit the collision/race the
real function is designed to avoid. Security/uniqueness proofs do NOT
transfer.

---

### 3.6 `shutil` — over fs (47 symbols)

**Unix grounding:** §5.3 (read/write), §4.1 (link count, unlink),
§4.4 (chmod/chown/utime for copystat), §3.4 (directory traversal for
rmtree).

| Core symbol | Bucket | Implementation |
|---|---|---|
| `copyfile` | **Modelled** | Read src inode bytes → write to dst inode |
| `copyfileobj` | **Modelled** | Stream-to-stream byte copy |
| `copy2` | **Modelled** | copyfile + copystat |
| `copystat` | **Modelled** | Copy inode metadata fields (mode, timestamps) |
| `rmtree` | **Modelled** | Recursive unlink + rmdir on fs |
| `which` | **Modelled** | PATH search with permission check (§4.3) |
| `SameFileError` | **Modelled** | Exception class |

**No new model class.** Every function composes existing `os`
primitives on `world.fs`. The main proof challenge is `rmtree` — it
needs loop invariants for recursive directory traversal.

**Cross-module postcondition now possible:** `after copyfile(src, dst):
world.fs.sys_read(dst_fd, n) == world.fs.sys_read(src_fd, n)` — this
is statable AND provable because src and dst share the same filesystem.

---

### 3.7 `hashlib` — HashModel (1 symbol)

**Unix grounding:** None (no kernel subsystem). Pure computation.

| Symbol | Bucket | Implementation |
|---|---|---|
| `sha256` | **Specified** | Uninterpreted hash function |

**HashModel fields:**
```python
class HashModel:
    _input_bytes: list[int]
    _digest_length: int = 32
```

The hash VALUE is an uninterpreted function — `ensures equal_input →
equal_output` is axiomatic. Only size contracts are modelled:
- `digest()`: `ensures \length(\result) == 32`
- `hexdigest()`: `ensures \length(\result) == 64`
- `update(data)`: `ensures \length(self._input_bytes) == \old(\length(self._input_bytes)) + \length(data)`

**TCB entry:** Any VC depending on the actual hash value (collision
resistance, a specific digest of specific bytes) proves nothing.

---

### 3.8 `__future__` (2 symbols) — pure constants

| Symbol | Bucket |
|---|---|
| `annotations` | **Modelled** — `_Feature(CO_FUTURE_ANNOTATIONS, 0x100000)` |
| `_Feature` | **Modelled** — class with `(compiler_flag, mandatory)` fields |

Trivial. Two integer constants.

---

### 3.9 `keyword` (1 symbol) — constant list

| Symbol | Bucket |
|---|---|
| `kwlist` | **Modelled** — list of Python keyword byte-arrays |

Trivial. A list literal.

---

### 3.10 `bisect` (2 symbols) — pure algorithm

**No Unix grounding needed.** Pure binary search.

| Symbol | Bucket |
|---|---|
| `bisect_left` | **Modelled** — classic binary search, integer-heavy |
| `key` | **Modelled** — key function parameter |

**Best ROI for body-level proof.** Classic algorithm with well-known
loop invariants. Fully provable.

```python
#@ requires 0 <= lo
#@ requires lo <= hi
#@ requires hi <= \length(a)
#@ ensures lo <= \result
#@ ensures \result <= hi
def bisect_left(a, x, lo, hi) -> int:
    ...
```

---

### 3.11 `enum` (2 symbols) — int class

| Symbol | Bucket |
|---|---|
| `IntEnum` | **Modelled** — integer with a name field |
| `auto` | **Modelled** — auto-incrementing counter |

---

### 3.12 `collections` (2 symbols) — array-based

| Symbol | Bucket |
|---|---|
| `defaultdict` | **Modelled** — dict with default factory |
| `deque` | **Modelled** — array-backed double-ended queue |

`deque` is integer-index arithmetic on a circular buffer. Body-level
provable. `defaultdict` wraps dict with a factory call.

---

### 3.13 `unicodedata` (2 symbols) — axiomatized

| Symbol | Bucket |
|---|---|
| `lookup` | **Specified** — name→character, axiomatic |
| `normalize` | **Specified** — idempotent normalization, axiomatic |

The Unicode database is too large to model as pure Python. Contracts
are axioms.

**TCB entry:** name/normalization facts are assumed, not proven.

---

### 3.14 `ast` (8 symbols) — stub + dump

| Symbol | Bucket |
|---|---|
| `parse` | **Stubbed** — CPython C API |
| `dump` | **Modelled** — recursive tree-to-string (string-heavy, likely specified body) |
| `_format` | **Modelled** — helper for dump |
| helper methods | **Stubbed** — list.append etc. |

---

### 3.15 `contextlib` (9 symbols) — pure logic

| Symbol | Bucket |
|---|---|
| `ExitStack` | **Modelled** — list of callbacks |
| `nullcontext` | **Modelled** — no-op context manager |
| `contextmanager` | **Specified** — generator protocol tricky for PyCSL |
| `_GeneratorContextManager` | **Specified** |
| helpers | **Stubbed** |

---

### 3.16 `copy` (15 symbols) — recursive with memo

| Symbol | Bucket |
|---|---|
| `deepcopy` | **Modelled but hard** — recursive with dispatch+memo dict |
| helpers | **Modelled** — dict lookups, isinstance checks |

**Aliasing caveat from v2:** `deepcopy` over arbitrary object graphs
needs sharing/cycle reasoning. This interacts with PyCSL's memory
model. Defer until the memory model (`typed`/`store`) supports it.

---

### 3.17 `inspect` (12 symbols) — stubs + cleandoc

| Symbol | Bucket |
|---|---|
| `unwrap` | **Modelled** — loop following `__wrapped__` chain |
| `cleandoc` | **Specified** — string-heavy indentation stripping |
| `signature` | **Stubbed** — delegates to `Signature.from_callable` |

---

### 3.18 `sysconfig` (41 symbols) — config dict

| Symbol | Bucket |
|---|---|
| `get_config_var` | **Modelled** — dict lookup |
| `get_config_vars` | **Modelled** — dict initialization + return |
| `get_paths` | **Modelled** — dict of paths with variable substitution |
| `_subst_vars` | **Specified** — string formatting |
| internal helpers | mix of **Modelled** (dict ops) and **Specified** (string) |

**Abstract model:** `_CONFIG_VARS` is a dict. No hardware model needed.

---

### 3.19 `typing` (52 symbols) — mostly stubbed

| Core symbol | Bucket |
|---|---|
| `cast` | **Modelled** — `return val` (identity, verifies nothing useful) |
| `get_type_hints` | **Stubbed** — introspection |
| `get_origin` / `get_args` | **Stubbed** |
| `overload` | **Stubbed** — decorator, no runtime effect |

Most of `typing` is introspection/metaclass machinery with no runtime
behavior worth proving.

---

### 3.20 `tokenize` (21 symbols) — character state machine

| Symbol | Bucket |
|---|---|
| core tokenizer | **Specified** — string-heavy, character-by-character |
| token constants | **Modelled** — integer constants |

String-heavy → mostly specified/stubbed for body verification.

---

### 3.21 `pathlib` (65 symbols) — string parsing + os delegation

| Core symbol | Bucket |
|---|---|
| Path joining/parsing | **Modelled** (string ops, likely specified bodies) |
| Filesystem methods | **Modelled** — delegate to `world.fs` (stat, mkdir, open...) |
| `Path.copy` / `Path.move` | **Modelled** — delegate to shutil |

High symbol count is mostly thin wrappers. Real coverage comes from
the underlying `os` model, not from Path methods themselves.

---

### 3.22 `dataclasses` (60 symbols) — thin API wrapper

| Core symbol | Bucket |
|---|---|
| `field` / `fields` | **Modelled** — data class + list |
| `_is_dataclass_instance` | **Modelled** — hasattr check |
| `@dataclass` decorator | **Stubbed** — uses `exec`/`type` (dynamic) |
| `_FuncBuilder` / `_process_class` | **Stubbed** |

The generative core (`exec`, dynamic class creation) is fundamentally
unverifiable. The API surface (`field`, `fields`, `replace`) is thin.

---

### 3.23 `argparse` (66 symbols) — thin API wrapper

| Core symbol | Bucket |
|---|---|
| `ArgumentParser.__init__` | **Modelled** — state initialization |
| `add_argument` | **Modelled** — append to action list |
| `parse_args` / `parse_known_args` | **Specified** — complex string matching |
| `ArgumentError` | **Modelled** — exception class |
| formatters, help | **Stubbed** |

String-heavy argument parsing → mostly specified. The data structures
(action lists, defaults dict) are modelled.

---

## 4. Soundness Ledger (TCB)

Every entry is added to the trusted computing base by a specified/stubbed
choice. This table is the honest answer to "what does a green run NOT
guarantee?"

| Where | Real property deleted/axiomatized | Consequence |
|---|---|---|
| `hashlib` | Hash value / collision resistance | Value-dependent VCs prove nothing |
| `unicodedata` | Unicode database | Name/normalization facts assumed |
| `ast.parse` | Parsing semantics | Downstream of `parse` is untyped |
| `subprocess` child | Program execution | Only pipe plumbing covered |
| `tempfile` names | Unpredictability / collision-freedom | Racy code can verify |
| `time` rate | Wall-clock duration | Only ordering modelled |
| `io` text | Encoding/decoding | String paths are stubs |
| `typing` | Type introspection | `cast` is identity, nothing proven |
| `dataclasses` | Dynamic class construction (`exec`) | Generative core unverified |
| `argparse` | String argument matching | Complex parsing is specified |

---

## 5. Implementation order

Foundations first (everything depends on them), then independent
integer-heavy wins, then façades, then string-heavy/hard cases.

| Phase | Module | Model | Symbols | Dominant bucket |
|---|---|---|---|---|
| **1. Foundation** | `time` | ClockModel | 1 | Modelled |
| | Wire fs↔clock in UnixInodeFileSystem | — | — | — |
| | World aggregate | {clock, fs, proc} | — | — |
| **2. Quick wins** | `bisect` | none | 2 | Modelled |
| | `keyword` | none | 1 | Modelled |
| | `enum` | none | 2 | Modelled |
| | `__future__` | none | 2 | Modelled |
| | `collections` | none | 2 | Modelled |
| | `unicodedata` | none | 2 | Specified |
| **3. Façades** | `sys` | ProcessState | 10 | Modelled |
| | `io` | StreamModel | 4 | Modelled + Specified |
| **4. Filesystem** | `tempfile` | over fs | 26 | Modelled |
| | `shutil` | over fs | 47 | Modelled |
| **5. Stubs** | `hashlib` | HashModel | 1 | Specified |
| | `ast` | none | 8 | Stubbed |
| | `contextlib` | none | 9 | Mixed |
| | `inspect` | none | 12 | Mixed |
| **6. Hard** | `copy` | none (aliasing) | 15 | Modelled-hard |
| | `subprocess` | ProcessModel | 93 | Modelled plumbing |
| **7. String-heavy** | `sysconfig` | config dict | 41 | Mixed |
| | `typing` | none | 52 | Stubbed |
| | `tokenize` | none | 21 | Specified |
| | `pathlib` | over fs | 65 | Mixed |
| | `dataclasses` | none | 60 | Stubbed |
| | `argparse` | none | 66 | Stubbed |

---

## 6. Open questions (from v2, retained)

1. **Memory-model fit.** Does PyCSL's `typed`/`store` model express
   references into a shared mutable World with sound `assigns`? If not,
   the resource-touching tier cannot be modelled coherently. Answer
   before Phase 3.

2. **Frame-condition scale.** As `assigns` clauses name World sub-parts,
   do they stay tractable, or does every cross-module call drag in the
   whole World?

3. **Stream aliasing.** What is the canonical buffer↔inode model so
   `io` writes and `os` reads on the same fd stay consistent?

4. **TCB growth.** Is the Soundness Ledger acceptable? Should a
   `--soundness-report` flag surface which VCs rest on specified/stubbed
   models?

5. **Coverage honesty.** Will coverage numbers be reported per bucket,
   so "proven" cannot be mistaken for "modelled"?

---

## 7. Relationship to existing code

| File | Status | v3 impact |
|---|---|---|
| `pure_lib/os/UnixInodeFileSystem.py` | 98.0% proven | Amend: accept ClockModel, expose fd_table |
| `pure_lib/os/__init__.py` | Done | No change |
| `pure_lib/re/_engine.py` | 16/16 formal VCs | No World dependency (pure logic) |
| `pure_lib/warn/__init__.py` | 18/18 body VCs | No World dependency (pure logic) |
| `pure_lib/json/_api.py` | 6/6 formal VCs | No World dependency (pure logic) |
| `pure_lib_test/formal_0001–0004.py` | Done | No change |
