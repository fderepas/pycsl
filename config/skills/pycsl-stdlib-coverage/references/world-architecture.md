# World architecture (placement reference)

Consult this when placing a new module in the World or checking its bucket/status: the ownership partition, the three-bucket classification detail, the per-module bucketing tables, the Soundness Ledger (TCB), the phased implementation order, and the directory/repo/verification-level architecture.

## Region-partitioned ownership

The World is **region-partitioned by ownership**, exactly as the Unix
on-disk layout is (superblock | inode table | data | bitmaps):

| Region | Owner | Who reads it |
|--------|-------|-------------|
| `world.fs.*` | fs methods (sys_open, sys_write, ...) | os, io, tempfile, shutil, subprocess |
| `world.proc.*` | proc methods (chdir, setenv, ...) | sys, subprocess |
| `world.clock.*` | `ClockModel.monotonic` | fs (for timestamps), time |

**Why this matters:** `sys`, `io`, `tempfile`, and `shutil` are
**not** independent modules with private state. They are **façades**
over the same kernel data. A file created through `tempfile.mkstemp()`
is the *same* inode that `os.stat()` observes, that `io.open()` reads,
that `shutil.copyfile()` duplicates. Cross-module postconditions like
"after copyfile, os.read(dst) == os.read(src)" are both statable and
sound because src and dst share the same filesystem.

## Three-bucket classification

Every symbol falls into exactly one bucket:

| Bucket | Meaning | VC value |
|--------|---------|----------|
| **Modelled** | Pure-Python stand-in preserving real semantics | Body emits as a WhyML `let`; its weakest-precondition VCs are discharged *Valid* by Alt-Ergo/Z3 |
| **Specified** | Axiomatized contract you trust (emits as a `val`, enters the TCB) | The contract is an assumption, not a VC — sound only for the stated properties |
| **Stubbed** | Signature only, no semantics | Proves nothing |

Coverage is **always reported per bucket**. A 100%-specified module
can show "100% proven" while guaranteeing nothing — a `val`'s contract
carries no VC of its own, so a green run there proves nothing about a
body. The headline "os: 1804/1804 VCs, 0 unproven" is meaningful because
those are modelled-bucket VCs — weakest-precondition obligations of real
`let` bodies that the solvers returned *Valid* on.

## Module-by-module bucketing

**World-touching modules (need abstract models):**

| Module | Symbols | Model | Dominant bucket |
|--------|---------|-------|-----------------|
| `time` | 1 | ClockModel | Modelled |
| `sys` | 10 | façade over proc + fd_table | Modelled |
| `io` | 4 | StreamModel (flush-through) | Modelled + Specified (text) |
| `subprocess` | 93 (~5 core) | ProcessModel + ProcessTable | Modelled plumbing / Stubbed child |
| `tempfile` | 26 | over fs (counter replaces randomness) | Modelled |
| `shutil` | 47 | over fs (compositions of os) | Modelled |
| `hashlib` | 1 | HashModel (uninterpreted value) | Specified |

**Pure-logic modules (no World dependency):**

| Module | Symbols | Dominant bucket |
|--------|---------|-----------------|
| `bisect` | 2 | Modelled (classic binary search) |
| `keyword` | 1 | Modelled (constant list) |
| `enum` | 2 | Modelled (int class + auto) |
| `__future__` | 2 | Modelled (constants) |
| `collections` | 2 | Modelled (deque, defaultdict) |
| `unicodedata` | 2 | Specified (Unicode DB axiomatized) |
| `ast` | 8 | dump Modelled / parse Stubbed |
| `contextlib` | 9 | ExitStack Modelled / contextmanager Specified |
| `copy` | 15 | Modelled-hard (aliasing/cycles) |
| `inspect` | 12 | unwrap Modelled / signature Stubbed |
| `sysconfig` | 41 | dict ops Modelled / string-heavy Specified |
| `typing` | 52 | cast Modelled (identity) / rest Stubbed |
| `tokenize` | 21 | Specified (string-heavy) |
| `pathlib` | 65 | path parse Specified / fs ops via World |
| `dataclasses` | 60 | field/fields Modelled / @dataclass Stubbed |
| `argparse` | 66 | state Modelled / parse_args Specified |

## Soundness Ledger (TCB)

What a green run does NOT guarantee:

| Where | What's trusted | Consequence |
|-------|---------------|-------------|
| `hashlib` | Hash value / collision resistance | Value-dependent VCs prove nothing |
| `unicodedata` | Unicode database | Name/normalization assumed |
| `ast.parse` | Parsing semantics | Downstream untyped |
| `subprocess` child | Program execution | Only plumbing covered |
| `tempfile` names | Unpredictability / collision-freedom | Racy code can verify |
| `time` rate | Wall-clock duration | Only ordering modelled |
| String-heavy paths | Encoding, string processing | Specified/stubbed |
| `typing` | Type introspection | `cast` proves nothing useful |
| `dataclasses` | Dynamic class construction (`exec`) | Generative core unverified |
| HAPPY `\preserves` | Trusted stubs preserve declared regions | Confinement theorem trusts these |

## Implementation order (phased)

| Phase | What | Notes |
|-------|------|-------|
| 1. Foundation | `time` → ClockModel; wire fs↔clock; `World` aggregate | Clock first — everything depends on it |
| 2. Confinement | Tier-1 ownership HAPPYs; extend HAPPY to nested fields | The coherence mechanism |
| 3. Quick wins | bisect, keyword, enum, __future__, collections, unicodedata | No World dependency |
| 3.5 Coarse probe | Cross-subsystem framing test | Should pass via Tier-1 HAPPY |
| 3.6 Fine probe (gate) | Intra-subsystem framing test | **Decides Tier-2 path before fs-mutating modules** |
| 4. Façades | sys, io (flush-through) | No direct fs writes |
| 5. Filesystem | tempfile, shutil | Use Tier-2 mechanism from 3.6 |
| 6. Stubs | hashlib, ast, contextlib, inspect | Specified/mixed |
| 7. Hard | copy (aliasing), subprocess | |
| 8. String-heavy | sysconfig, typing, tokenize, pathlib, dataclasses, argparse | Mostly specified/stubbed |

---

## Architecture

### Directory layout

```text
pure_lib/
  os/
    __init__.py              # Re-exports, constants (literal values)
    UnixInodeFileSystem.py   # Full inode filesystem (~1090 lines)
  re/
    __init__.py              # Re-exports RePattern as Pattern, etc.
    _engine.py               # 7 hand-written matchers, Pattern, ReMatch
  warn/
    __init__.py              # Functions directly here (not submodule!)
  json/
    __init__.py              # Original json implementation
    _api.py                  # Thin verifiable API wrapper
    decoder.py, encoder.py   # Full impl (body-level blocked)
pure_lib_test/                 # ALL formal tests use the topical `formal_<name>.py` scheme
  formal_os_roundtrip.py       # os write/read round-trip (18/18 VCs)
  formal_os_content.py         # os CONTENT round-trip (write→pread == data, gap-17)
  formal_os_*.py               # per-topic os: _dir/_fd/_fdchain/_io/_namespace/_rwsize/…
  formal_re_engine.py          # re engine + escape
  formal_warn_filter.py        # warnings simplefilter/_deprecated
  formal_json_codec.py         # json detect_encoding/loads/dumps
  formal_<module>.py           # one per stdlib module (re/json/dt/itools/…)
lib/
  calling.json               # Call graph: which stdlib symbols to cover
```

### Two verification levels

1. **Body-level** — the function emits as a WhyML `let`; Why3 generates
   its weakest-precondition VCs and the solvers discharge them. Works
   best for integer-heavy code (os filesystem, warnings). Requires the
   full function body to compile to valid WhyML.

2. **Stub-level** — PyCSL generates `val` declarations (abstract
   function specs, contract-only, no body and no VC of their own) from
   `__init__.py` imports; their contracts become caller assumptions.
   Formal tests verify properties through these stubs. Works for
   string-heavy code (re) or partially-verifiable modules (json) where
   body-level verification hits tool gaps.

3. **Thin API wrapper** (new pattern from json) — When most of a module
   fails body-level proof, create a `_api.py` with:
   - Body-verified functions for simple logic (integer ops only)
   - Stub wrappers that delegate to the real implementation for complex code
   - This gives you *some* body-level proof without fighting the tool
