# Making It Pure: Abstract Models for Every Stdlib Module

Every stdlib module used by PyCSL can be given a pure-Python
implementation by modelling the underlying hardware/environment as a
Python data structure — exactly as `UnixInodeFileSystem` models the
Unix inode layer for `os`.

This document details which abstract models need to be created for
each remaining module.

---

## Precedent: how UnixInodeFileSystem works

`pure_lib/os/UnixInodeFileSystem.py` models:
- **Inodes** as fixed-size arrays (`[type, link_count, size, ...]`)
- **Data blocks** as a flat array of bytes
- **Free bitmap** as an array of 0/1 flags
- **File descriptors** as `[inode_num, offset, flags]` triples
- **Directory entries** as arrays of `[name_bytes, inode_num]` pairs

Every `os` function (`open`, `read`, `write`, `mkdir`, `stat`, ...) is
a method that manipulates these arrays with pure integer arithmetic.
Result: 98.0% of 4101 VCs proven by body-level verification.

The same approach applies to all modules below.

---

## Tier 1 — Modules needing an environment/hardware model

### `sys` — PythonRuntimeState (10 symbols)

**What to model:** The Python interpreter's runtime state.

**Abstract model: `PythonRuntimeState`**
```
Fields:
  _argv: list[list[int]]    # sys.argv — list of byte arrays
  _path: list[list[int]]    # sys.path — list of byte arrays (module search paths)
  _stdin_buffer: list[int]  # bytes available on stdin
  _stdin_pos: int            # current read position in stdin
  _stderr_buffer: list[int] # accumulated stderr output
  _exit_code: int            # set by sys.exit()
  _float_max_10_exp: int     # sys.float_info.max_10_exp (constant: 308)
```

**APIs to implement:**
- `argv` → return `self._argv`
- `path` → return `self._path`
- `path.insert(i, p)` → list insert on `self._path`
- `exit(code)` → set `self._exit_code`, raise SystemExit
- `stdin` / `stdin.buffer` / `stdin.buffer.read()` → read from `_stdin_buffer`
- `stderr` → write to `_stderr_buffer`
- `float_info.max_10_exp` → return `self._float_max_10_exp` (constant 308)

**Complexity:** Low. Mostly state reads. Integer-heavy.

---

### `io` — StreamModel (4 symbols)

**What to model:** Byte/text stream I/O abstraction.

**Abstract model: `StreamModel`**
```
Fields:
  _buffer: list[int]       # underlying byte buffer
  _pos: int                # current read/write position
  _mode: int               # read/write/append flags
  _encoding: int           # text encoding identifier
  _closed: bool            # whether the stream is closed
```

**APIs to implement:**
- `StringIO()` → create a `StreamModel` in text mode with empty buffer
- `TextIOWrapper(buffer, encoding)` → wrap a byte-level `StreamModel` with encoding
- `open(name, mode)` → delegate to the filesystem model (`UnixInodeFileSystem`) + wrap in `StreamModel`
- `text_encoding(encoding)` → normalize encoding name (pure logic)

**Dependency:** Shares filesystem with `UnixInodeFileSystem` (io.open
produces a stream backed by the inode model). Could take `UnixInodeFileSystem`
as a constructor parameter.

**Complexity:** Medium. Buffer arithmetic is integer-heavy (provable). Text
encoding/decoding is string-heavy (stub-level).

---

### `subprocess` — ProcessModel (93 symbols, but ~5 core APIs)

**What to model:** Child process creation and management.

**Abstract model: `ProcessModel`**
```
Fields:
  _pid: int                  # process ID
  _returncode: int           # exit code (-1 = still running)
  _stdin_pipe: list[int]     # bytes written to child's stdin
  _stdout_pipe: list[int]    # bytes produced by child on stdout
  _stderr_pipe: list[int]    # bytes produced by child on stderr
  _args: list[list[int]]     # command + arguments
  _env: list[list[int]]      # environment variables
  _cwd: int                  # working directory (inode number)
```

**`ProcessTable`** (environment-level model):
```
Fields:
  _processes: list[ProcessModel]  # all spawned processes
  _next_pid: int                  # PID counter
  _fs: UnixInodeFileSystem        # shared filesystem reference
```

**APIs to implement:**
- `Popen(args, ...)` → create a `ProcessModel`, add to `ProcessTable`
- `process.communicate()` → return `(stdout_pipe, stderr_pipe)`, set `_returncode`
- `process.poll()` → return `_returncode` if finished, -1 otherwise
- `process.wait()` → block until `_returncode >= 0`
- `run(args, ...)` → `Popen` + `communicate` + wrap in `CompletedProcess`
- `CalledProcessError`, `TimeoutExpired` → exception classes
- `list2cmdline(args)` → pure string joining (integer-heavy)

**Note:** Most of the 93 symbols are internal helpers, platform-specific
branches (winapi), or method calls on objects. The core API surface is
~5 functions. The model abstracts away actual process execution — a child
process is just a state machine with pipes.

**Complexity:** Medium-high for the full API, but the core (Popen/run/communicate)
is tractable. Platform-specific branches (Windows handles, fcntl) are dropped
from the model — we model POSIX only, like `UnixInodeFileSystem`.

---

### `tempfile` — TempFileModel (26 symbols)

**What to model:** Temporary file creation on the filesystem.

**Abstract model:** Extends `UnixInodeFileSystem` with temp-directory
tracking. No separate hardware — temp files are just regular files
in a designated directory.

```
Additional fields (on UnixInodeFileSystem or wrapper):
  _tempdir: int              # inode of the temp directory
  _name_counter: int         # deterministic name generator (replaces randomness)
```

**APIs to implement:**
- `mkstemp(suffix, prefix, dir)` → create a file in `_tempdir` via
  `UnixInodeFileSystem.open()`, return `(fd, path)`
- `gettempdir()` → return path to `_tempdir`
- `NamedTemporaryFile(...)` → `mkstemp` + wrapper with auto-delete
- `_TemporaryFileWrapper` → thin wrapper around fd with `close` → `unlink`
- `_get_default_tempdir()` → return `_tempdir` path
- `_candidate_tempdir_list()` → return `[_tempdir]`

**Dependency:** Directly uses `UnixInodeFileSystem`. Temp files are just
files. The "randomness" in name generation is replaced by a counter
(deterministic, provable).

**Complexity:** Low. Thin layer over filesystem model.

---

### `shutil` — high-level file operations (47 symbols)

**What to model:** No new hardware model needed. `shutil` is
a high-level API over `os` operations (copy, move, remove).

**Abstract model:** None — operates directly on `UnixInodeFileSystem`.

**APIs to implement:**
- `copyfile(src, dst)` → read all bytes from src inode, write to dst inode
- `copyfileobj(fsrc, fdst)` → copy bytes between stream models
- `copy2(src, dst)` → `copyfile` + copy metadata (permissions, timestamps)
- `copystat(src, dst)` → copy inode metadata fields
- `rmtree(path)` → recursive `unlink` + `rmdir` on `UnixInodeFileSystem`
- `which(name)` → search `PATH` entries for executable (permission check)
- `SameFileError`, `SpecialFileError` → exception classes

**Complexity:** Medium. Lots of functions but each one is a composition
of `os` primitives already proven. The main challenge is recursive
directory traversal (`rmtree`), which needs loop invariants.

---

### `time` — ClockModel (1 symbol)

**What to model:** A monotonic clock.

**Abstract model: `ClockModel`**
```
Fields:
  _ticks: int    # monotonically increasing counter
```

**APIs to implement:**
- `monotonic()` → return `self._ticks`, then increment

**Contract:** `ensures \result >= 0`, `ensures \result > \old(_ticks)`

**Complexity:** Trivial. One field, one function, one postcondition.

---

### `hashlib` — HashModel (1 symbol)

**What to model:** A cryptographic hash function (SHA-256).

**Abstract model: `HashModel`**
```
Fields:
  _input_bytes: list[int]   # accumulated input
  _digest_length: int       # always 32 for SHA-256
```

We do NOT need to implement the SHA-256 algorithm. We model the
**contract**: the hash function takes bytes and produces a fixed-length
digest. The key provable property is determinism: same input → same output.

**APIs to implement:**
- `sha256(data)` → create `HashModel` with `_input_bytes = data`
- `.digest()` → return a list of length `_digest_length`
- `.hexdigest()` → return a string of length `_digest_length * 2`
- `.update(data)` → extend `_input_bytes`

**Contract properties:**
- `ensures \length(\result) == 32` (digest)
- `ensures \length(\result) == 64` (hexdigest)
- Determinism: abstract axiom that equal inputs produce equal outputs

**Complexity:** Low. The hash itself is axiomatic (uninterpreted function).
The interesting properties are input/output size contracts.

---

## Tier 2 — Modules needing pure logic only (no hardware model)

These modules operate on pure data — no OS, no I/O, no hardware.
They need no abstract model class, just pure-Python implementations.

### `__future__` (2 symbols)
- `annotations` — a feature flag, modeled as a constant
- `_Feature` — a trivial class with `(compiler_flag, mandatory)` fields
- **Complexity:** Trivial.

### `ast` (8 symbols)
- `parse(source)` → stub (delegates to `compile()` which is a CPython C API)
- `dump(node)` → pure recursive tree-to-string formatter
- **Complexity:** Low. `dump` is recursive string building. `parse` is a stub.

### `bisect` (2 symbols)
- `bisect_left(a, x, lo, hi)` → pure binary search (integer-heavy!)
- **Complexity:** Trivial. Classic algorithm. Body-level provable.

### `collections` (2 symbols)
- `defaultdict` → dict wrapper with default factory
- `deque` → double-ended queue on array
- **Complexity:** Low-medium. Array manipulation, integer indices.

### `contextlib` (9 symbols)
- `contextmanager` → decorator wrapping a generator into `__enter__/__exit__`
- `ExitStack` → list of cleanup callbacks
- `nullcontext` → no-op context manager
- **Complexity:** Medium. Generator protocol is tricky for PyCSL, but
  `ExitStack` and `nullcontext` are pure logic.

### `copy` (15 symbols)
- `deepcopy(obj)` → recursive object copy with memo dict
- **Complexity:** Medium. Recursive with dispatch table. The dispatch
  logic is pure dict lookup + recursion.

### `dataclasses` (60 symbols)
- Metaclass machinery for `@dataclass` decorator
- Heavy use of `exec()`, `type()`, introspection
- **Complexity:** High. Many symbols but most are internal helpers.
  The verifiable core is `field()` + `fields()` + `_is_dataclass_instance()`.
  Decorator machinery (`exec`, dynamic class creation) will be stub-level.

### `enum` (2 symbols)
- `IntEnum` → integer subclass with named constants
- `auto()` → auto-incrementing value generator
- **Complexity:** Low. Model as a class with int fields.

### `inspect` (12 symbols)
- `signature(fn)` → function signature introspection
- `cleandoc(doc)` → pure string processing (strip indentation)
- `unwrap(fn)` → follow `__wrapped__` chain
- **Complexity:** Medium. `cleandoc` is string-heavy (stub-level).
  `signature` delegates to `Signature.from_callable` (stub).
  `unwrap` is a loop following attribute chains.

### `keyword` (1 symbol)
- `kwlist` → a constant list of Python keyword strings
- **Complexity:** Trivial. A list literal.

### `pathlib` (65 symbols)
- `Path` class with filesystem operations
- **Dependency:** Delegates to `os` operations under the hood
- **Complexity:** High symbol count but most methods are thin
  wrappers around `os.stat`, `os.mkdir`, `os.open`, etc. The pure-logic
  part (path parsing, joining, splitting) is string manipulation.
  Filesystem operations reuse `UnixInodeFileSystem`.

### `sysconfig` (41 symbols)
- Python build configuration access
- **Abstract model:** A configuration dict — `_CONFIG_VARS` is just a
  `dict[str, str]`. No hardware needed.
- `get_config_var(name)` → dict lookup
- `get_paths(scheme)` → dict of path templates with variable substitution
- **Complexity:** Medium. Lots of string formatting (`_subst_vars`).
  The core is dict lookups (integer-heavy if keys are ints).

### `tokenize` (21 symbols)
- Python source tokenizer
- Pure string/character processing
- **Complexity:** Medium-high. Character-by-character parsing with
  state machine. String-heavy → likely stub-level for body verification.

### `typing` (52 symbols)
- Type annotation utilities
- `get_type_hints`, `get_origin`, `get_args`, `cast`, `overload`
- **Complexity:** Medium. Most functions are introspection wrappers.
  Many can be modeled as identity functions or dict lookups.
  `cast(typ, val)` is literally `return val`.

### `unicodedata` (2 symbols)
- `lookup(name)` → Unicode character by name (stub: axiomatic)
- `normalize(form, s)` → Unicode normalization (stub: axiomatic)
- **Complexity:** Trivial as stubs. The Unicode database itself is not
  modelable as pure Python (too large), but the contract (name → char,
  idempotence of normalization) is.

---

## Tier 3 — Large modules: thin API wrapper pattern

For `argparse` (66 symbols), `subprocess` (93 symbols), `pathlib`
(65 symbols), `dataclasses` (60 symbols), and `typing` (52 symbols):
use the **thin API wrapper** pattern proven with `json/_api.py`.
Create `_api.py` with:
- Body-verified functions for logic that is integer/boolean-heavy
- Stub wrappers for the rest (delegating to the full implementation)

This gives partial body-level coverage without fighting every tool gap.

---

## Summary of abstract models needed

| Module | Abstract model | Models what |
|--------|---------------|-------------|
| `os` | `UnixInodeFileSystem` ✅ | Inodes, data blocks, FDs, directories |
| `sys` | `PythonRuntimeState` | argv, path, stdin/stderr, exit code |
| `io` | `StreamModel` | Byte/text stream buffers, position, mode |
| `subprocess` | `ProcessModel` + `ProcessTable` | PIDs, pipes, exit codes |
| `tempfile` | (extends `UnixInodeFileSystem`) | Temp directory + name counter |
| `shutil` | (uses `UnixInodeFileSystem`) | No new model — high-level os ops |
| `time` | `ClockModel` | Monotonic tick counter |
| `hashlib` | `HashModel` | Input accumulator + fixed-length digest |
| `sysconfig` | (config dict) | Build configuration key-value store |

All other modules (bisect, collections, copy, enum, keyword, etc.)
need **no hardware model** — they are pure logic implementable directly
in Python.

---

## Implementation order (recommended)

Priority: maximize coverage with minimum effort, integer-heavy first.

1. **time** (1 symbol, trivial model) → `ClockModel`
2. **hashlib** (1 symbol, trivial model) → `HashModel`
3. **keyword** (1 symbol, no model) → constant list
4. **bisect** (2 symbols, no model) → pure algorithm
5. **enum** (2 symbols, no model) → int class
6. **__future__** (2 symbols, no model) → constants
7. **unicodedata** (2 symbols, no model) → axiomatic stubs
8. **collections** (2 symbols, no model) → array-based deque + defaultdict
9. **sys** (10 symbols) → `PythonRuntimeState`
10. **io** (4 symbols) → `StreamModel`
11. **contextlib** (9 symbols, no model) → pure logic
12. **inspect** (12 symbols, no model) → stubs + cleandoc
13. **copy** (15 symbols, no model) → recursive with memo
14. **ast** (8 symbols, no model) → stubs + dump
15. **tempfile** (26 symbols) → extend filesystem model
16. **shutil** (47 symbols) → compose os operations
17. **sysconfig** (41 symbols) → config dict
18. **typing** (52 symbols) → mostly identity/introspection
19. **tokenize** (21 symbols) → character state machine
20. **pathlib** (65 symbols) → string parsing + os delegation
21. **dataclasses** (60 symbols) → thin API wrapper
22. **argparse** (66 symbols) → thin API wrapper
23. **subprocess** (93 symbols) → `ProcessModel` + thin API wrapper
