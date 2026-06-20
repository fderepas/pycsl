# Status and running

Consult this when invoking the PyCSL tool (the exact commands, import-resolution/CWD rules, provers) or when picking the next module to cover (per-module current status + the phased "what to cover next").

## Current status

### os module — 100% proven (body-level), 0 unproven

| Metric | Value |
|--------|-------|
| Valid VCs | 1804 |
| Unproven goals | **0** |
| Proven rate | **100%** (body-level) |
| TCB | 1 cross-validated axiom (a bitwise bound) |
| Formal test | `formal_os_roundtrip` 18/18 VCs ✅ (totality/safety, all symbolic inputs) |

The `os` module — a Unix inode filesystem in `src/pycsl_lib/os/` — is **fully proven** body-level: every
syscall, the codec leaves, the inode round-trip, the read-after-write recovery, and the on-disk layout
class invariant all discharged by SMT, on a one-line trusted base. The earlier `subscript_get` gap and
the 23 disk-mutating syscalls were closed — leaf-first VALUE contracts + `#@ no_inline` modular
boundaries (prove a syscall once, reuse its contract) + the codec extracted to its own minimal-context
file so the inode round-trip proves inline (eliminating its axiom). The **content round-trip**
(`formal_os_content`, `#@ ensures \result == True` — read-back equals what was written, via the folded
`block_content_eq` atom that crosses the no_inline boundary) is **PROVEN** through the public API
(write→pread == data). The remaining functional-correctness frontier is the cross-call REOPEN-by-name
version (create→write→close→reopen→read), which needs data-block recovery across close/open. The full
methodology — and `os` as its worked example — is in `docs/formal-filesystem.md`.

### re module — 16/16 formal test VCs (stub-level)

| Metric | Value |
|--------|-------|
| Formal test VCs | 16/16 ✅ |
| Body-level proof | Blocked (R10–R13) |
| Concrete test | 10/10 pass |
| Matchers annotated | 7/7 |

Body-level proof blocked by string operation gaps (missing
`use string.String`, `isdigit()` receiver loss, class-return type
mismatch). Stub-level verification through `__init__.py` works well.

### warnings module — 18/18 body-level + 3/3 formal (body-level)

| Metric | Value |
|--------|-------|
| Body-level VCs | 18/18 ✅ |
| Formal test VCs | 3/3 ✅ |
| Concrete test | 5/5 pass |
| Functions | 4 (warn, simplefilter, _deprecated, catch_warnings) |

Named `warn/` to avoid stdlib name clash. Functions live directly in
`__init__.py` because function contracts don't propagate through
re-exports. `warn()` excluded from formal test because it raises
`Exception` and formal tests can't declare `raises`.

### json module — 6/6 formal test VCs (thin API wrapper)

| Metric | Value |
|--------|-------|
| Formal test VCs | 6/6 ✅ |
| Concrete test | 15/15 pass |
| Body-level proof | Partially blocked |
| Pattern | Thin `_api.py` wrapper |

Body-level proof blocked by: inliner method argument count mismatch
(`iterencode`), tuple parameter destructuring, encoder pipeline crash.
`detect_encoding` is body-verified (integer ops only). `loads`/`dumps`
are stubs delegating to real implementation.

---

## How to run PyCSL

### Import resolution (critical)

PyCSL resolves imports by searching: (1) the file's directory, (2) CWD,
(3) built-in `Lib/`. This means **CWD controls which `src/pycsl_lib/` is
found**.

The models live in this repo under `src/pycsl_lib/<module>/` and the formal
tests under `src/pycsl_lib_test/`. Run from the repo root.

```bash
cd /path/to/pycsl
.venv/bin/python3 src/pycsl/pycsl.py --keep-mlw src/pycsl_lib/os/__init__.py
# or a formal test:
.venv/bin/python3 src/pycsl/pycsl.py --keep-mlw src/pycsl_lib_test/formal_os_namespace.py
```

- `--keep-mlw`: preserve generated `.mlw` file for inspection
- `--no-proof`: skip proof, only check WhyML generation
- `PYTHONHASHSEED=0`: required for deterministic output
- Provers: Alt-Ergo 2.6.2 (primary), Z3 4.13.3 (fallback)

---

## What to cover next

The `lib/calling.json` file lists all stdlib symbols PyCSL uses.
Modules covered so far: `os`, `re`, `warnings`, `json`. The remaining
23 modules (542 symbols) follow the phased implementation order above.

**Current phase: Foundation (Phase 1).** Build `ClockModel`, wire
fs↔clock, define the `World` aggregate. Then Phase 2 (confinement
HAPPYs) and Phase 3 (quick wins: bisect, keyword, enum, etc.).

**The gate (Phase 3.6):** The fine probe — can PyCSL prove that
writing inode A preserves inode B? — decides whether Phase 5
(tempfile, shutil) uses parametric HAPPY or a narrow `assigns`
fallback. This is the make-or-break question; answer it before
building any fs-mutating module.
