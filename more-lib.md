# more-lib.md — Stdlib Expansion Plan

## Methodology

Analysed all pure-Python CPython 3.14 stdlib modules.  
Criterion: **all pure-Python deps already modelled in `pure_lib/`**, minimal C-extension surface.

---

## Tier 1 — Trivially Addable (zero missing pure deps, ≤1 C dep)

| Module | Lines | Funcs | Pure deps (satisfied) | C dep | Notes |
|--------|------:|------:|----------------------|-------|-------|
| **colorsys** | 166 | 7 | — | — | Pure arithmetic (RGB↔HSV↔HLS). Ideal first target. |
| **textwrap** | 475 | 14 | `re` | — | Text wrapping/filling/dedent. Pure text transforms. |
| **html** | 132 | 3 | `re` | — | `escape()`/`unescape()` — tiny, pure. |
| **linecache** | 256 | 13 | `os`, `sys`, `tokenize` | — | Source line caching. Uses os/tokenize already modelled. |
| **string** | 325 | 21 | `collections`, `re` | `_string` | Constants + `Template` + `Formatter`. C dep is fallback only. |
| **signal** | 94 | 10 | `enum` | `_signal` | Signal constants via IntEnum. C dep is the runtime dispatch. |
| **struct** | 15 | 0 | — | `_struct` | Thin wrapper around C — just export stubs. |

**Estimated effort**: 1–3 hours each. All can be contract-only (`\trusted` bodies for
functions touching C) or body-proven (colorsys, textwrap, html are pure arithmetic/text).

### Priority order

1. **colorsys** — 7 pure-math functions, zero deps, perfect for full body-level proof
2. **html** — 3 functions, `re` dep already satisfied, small and self-contained
3. **textwrap** — 14 functions, `re` dep satisfied, useful for formatting proofs
4. **string** — `capwords()` trivial; `Template` needs `re`; `_string` C dep is cosmetic
5. **linecache** — 13 functions, all deps met; touches files (model via existing `os`)
6. **signal** — mostly constants; C-backed dispatch is `\trusted`
7. **struct** — pure wrapper; just stub signatures with byte-length postconditions

---

## Tier 2 — Moderate (zero missing pure deps, 2 C deps)

| Module | Lines | Funcs | Pure deps (satisfied) | C deps | Notes |
|--------|------:|------:|----------------------|--------|-------|
| **abc** | 188 | 11 | — | `_abc`, `_py_abc` | ABC mechanism. `_py_abc` is pure fallback. |
| **decimal** | 109 | 0 | `sys` | `_decimal`, `_pydecimal` | Dispatcher to C impl; `_pydecimal.py` is 6000L pure Python. |

**abc** is important as a dependency for `numbers`, `collections.abc`, etc.
Model the pure `_py_abc` fallback with `\trusted` on the C accelerator.

---

## Tier 3 — One Missing Pure Dep (chain-unlocks)

| Module | Lines | Funcs | Missing dep | Unlocked by | Notes |
|--------|------:|------:|-------------|-------------|-------|
| **getopt** | 240 | 9 | `gettext` | stub gettext | CLI option parsing — `gettext` is cosmetic (i18n). |
| **pprint** | 675 | 41 | `types` | stub types | Pretty-printing — `types` is just `types.SimpleNamespace`. |
| **ipaddress** | 2417 | 140 | `functools` | Tier 4 functools | IP address manipulation — pure integer/bit math. |
| **numbers** | 427 | 56 | `abc` | Tier 2 abc | Abstract numeric tower. |
| **operator** | 475 | 69 | `functools` | Tier 4 functools | Standard operators — bodies are one-liners. |
| **csv** | 513 | 17 | `types` | stub types | CSV parsing. C accel optional. |
| **heapq** | 611 | 17 | `doctest` | ignore (test-only) | Heap algorithms — pure list manipulation. Doctest import is guarded. |

### Quick wins via minimal stubs

- **`gettext`** (stub `gettext()` as identity) → unlocks `getopt`, `optparse`
- **`types`** (stub `SimpleNamespace`, `ModuleType`) → unlocks `pprint`, `csv`, `difflib`
- **`heapq`** already importable if we skip the `doctest` import (it's `if __name__`)

---

## Tier 4 — Heavy Deps (future, after tool bugs fixed)

| Module | Key blockers |
|--------|-------------|
| functools | abc, operator, types, weakref + 2 C deps |
| configparser | functools, itertools (C) |
| difflib | heapq, types |
| glob | fnmatch, functools, itertools, operator, stat |
| random | itertools (C), math (C), operator, statistics |
| traceback | linecache, textwrap, itertools, difflib |
| threading | itertools (C) + 5 C deps |

These require either modelling C-extension modules (`itertools`, `math`) as `\trusted`
stubs or waiting for tool maturity.

---

## Recommended Execution Order

```
Phase 1 (body-proven, zero blockers):
  colorsys → html → textwrap → string.capwords

Phase 2 (contract-only, minimal C stubs):
  signal → struct → linecache

Phase 3 (unlock chain):
  abc → numbers
  stub types → pprint, csv
  stub gettext → getopt
  heapq (skip doctest guard)

Phase 4 (after functools lands):
  ipaddress → operator → fnmatch → glob → optparse
```

---

## Verification Targets

| Phase | New VCs (est.) | Body-proven | Contract-only |
|-------|---------------|-------------|---------------|
| 1 | ~30 | colorsys(14), html(6), textwrap(~10) | — |
| 2 | ~15 | — | signal(10), struct(3), linecache(2) |
| 3 | ~40 | heapq(~17), pprint(~6) | abc(5), numbers(5), getopt(7) |
| 4 | ~80 | ipaddress(~50), operator(~30) | — |

**Total potential**: ~165 new VCs across ~20 new modules.

---

## Prerequisites

- Tool bugs 07-1321 (bytes/array-ref) are NOT blocking for Tier 1–3
  (these modules don't use `bytes()` constructor or mutable array locals)
- `itertools` and `math` remain C-only; model as `\trusted` stubs when needed
- Each new module gets: `pure_lib/<short>/`, `__init__.py`, test in `pure_lib_test/`
