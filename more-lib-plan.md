# more-lib-plan.md — Execution Plan for Stdlib Expansion

## Goal

Deliver ~165 new proven VCs across ~20 new pure-Python stdlib modules,
expanding PyCSL formal coverage from 27 → 47 modules.

---

## Conventions

Each new module follows the established pattern:

```
pure_lib/<short>/__init__.py    # PyCsl-annotated model
pure_lib_test/NNNN.py           # Concrete (pytest) test
pure_lib_test/formal_NNNN.py    # Formal (pycsl) test
```

**Short names** avoid stdlib name clashes (e.g. `tm` for `time`, `hlib` for `hashlib`).

**Completion criterion** for each module:
1. `pycsl` reports "All contracts formally proven" on the module file
2. `pycsl` reports success on the formal test file
3. Concrete test passes with `pytest`

---

## Phase 1 — Pure-Arithmetic / Pure-Text (body-proven)

No external deps except already-modelled `re`. Full body-level proof expected.

### 1.1 colorsys → `csys`

| Item | Detail |
|------|--------|
| Functions | `rgb_to_yiq`, `yiq_to_rgb`, `rgb_to_hls`, `hls_to_rgb`, `rgb_to_hsv`, `hsv_to_rgb` |
| Deps | None |
| Contracts | `requires` 0 ≤ r,g,b ≤ 1; `ensures` result in [0,1] (or [-1,1] for yiq) |
| Body proof | Full — all functions are closed-form arithmetic |
| Est. VCs | 14 (2 per function: precondition + postcondition) |
| Test | `formal_csys.py`: round-trip `rgb→hsv→rgb` preserves values |

### 1.2 html → `htmlm`

| Item | Detail |
|------|--------|
| Functions | `escape(s)`, `unescape(s)` |
| Deps | `re` (already modelled) |
| Contracts | `ensures \result >= 0` (length); escape idempotent on safe strings |
| Body proof | Full for `escape`; `unescape` may need `\trusted` (regex callback) |
| Est. VCs | 6 |
| Test | `formal_htmlm.py`: escape('&') returns '&amp;' model |

### 1.3 textwrap → `txtwrp`

| Item | Detail |
|------|--------|
| Functions | `wrap`, `fill`, `shorten`, `dedent`, `indent` |
| Deps | `re` (already modelled) |
| Contracts | `ensures \result >= 0` (list length); `dedent` preserves content |
| Body proof | `dedent`, `indent` body-provable; `wrap/fill/shorten` contract-only |
| Est. VCs | 10 |
| Test | `formal_txtwrp.py`: dedent + indent round-trip |

### 1.4 string → `strmod`

| Item | Detail |
|------|--------|
| Functions | `capwords` |
| Classes | `Template` (contract-only), `Formatter` (contract-only) |
| Deps | `collections`, `re` (both modelled) |
| Contracts | capwords postcondition on word count; Template.substitute ensures result >= 0 |
| Body proof | `capwords` body-provable |
| Est. VCs | 8 |
| Test | `formal_strmod.py`: capwords correctness |

**Phase 1 deliverable**: 4 modules, ~38 VCs, all body-proven where possible.

---

## Phase 2 — Contract-Only with Minimal C Stubs

### 2.1 signal → `sig`

| Item | Detail |
|------|--------|
| Functions | Constants (`SIGINT`, `SIGTERM`, …), `signal()`, `raise_signal()` |
| Deps | `enum` (modelled) |
| C dep | `_signal` — all dispatch is C-backed |
| Contracts | `requires sig_num > 0`; signal numbers are valid IntEnum |
| Body proof | None (C runtime dispatch) |
| Est. VCs | 5 |
| Test | `formal_sig.py`: signal number validity |

### 2.2 struct → `strct`

| Item | Detail |
|------|--------|
| Functions | `pack`, `unpack`, `calcsize` |
| Deps | None |
| C dep | `_struct` — entire implementation is C |
| Contracts | `calcsize` postcondition ≥ 0; `unpack` returns tuple of correct length |
| Body proof | None (pure stubs) |
| Est. VCs | 4 |
| Test | `formal_strct.py`: calcsize('ii') == 8 model |

### 2.3 linecache → `lcache`

| Item | Detail |
|------|--------|
| Functions | `getline`, `getlines`, `clearcache`, `checkcache` |
| Deps | `os`, `sys`, `tokenize` (all modelled) |
| Contracts | `getline` ensures result >= 0; `getlines` ensures list result |
| Body proof | `clearcache` trivially provable; others contract-only |
| Est. VCs | 6 |
| Test | `formal_lcache.py`: getlines length consistency |

**Phase 2 deliverable**: 3 modules, ~15 VCs.

---

## Phase 3 — Chain-Unlock (new stubs enable groups)

### 3.0 Prerequisite stubs

Before Phase 3 modules, create minimal stubs:

- **`types_stub`** (`pure_lib/types_stub/__init__.py`):
  `SimpleNamespace`, `ModuleType`, `FunctionType` — empty classes with `\trusted` constructors.

- **`gettext_stub`** (`pure_lib/gettext_stub/__init__.py`):
  `gettext(s) -> s` (identity function — no i18n in proofs).

These are ≤10 lines each, zero VCs (pure stubs).

### 3.1 abc → `abcmod`

| Item | Detail |
|------|--------|
| Functions | `abstractmethod` (decorator), `update_abstractmethods` |
| Classes | `ABC`, `ABCMeta` |
| Deps | None (C dep `_abc` is accelerator; `_py_abc` fallback is pure) |
| Contracts | `abstractmethod` returns its argument; ABC has no instances |
| Body proof | `abstractmethod` is trivial; ABCMeta is contract-only |
| Est. VCs | 5 |

### 3.2 numbers → `nums`

| Item | Detail |
|------|--------|
| Classes | `Number`, `Complex`, `Real`, `Rational`, `Integral` |
| Deps | `abc` (Phase 3.1) |
| Contracts | Numeric tower: `Integral ⊂ Rational ⊂ Real ⊂ Complex ⊂ Number` |
| Body proof | Mostly abstract — register operations as `\trusted` |
| Est. VCs | 8 |

### 3.3 heapq → `hq`

| Item | Detail |
|------|--------|
| Functions | `heappush`, `heappop`, `heapify`, `heapreplace`, `nlargest`, `nsmallest` |
| Deps | None (doctest import is guarded by `__name__` check — skip) |
| C dep | `_heapq` accelerator (pure fallback exists in same file) |
| Contracts | heap invariant: `h[k] <= h[2k+1]` and `h[k] <= h[2k+2]`; push/pop maintain invariant |
| Body proof | Sift-up/sift-down loops — need loop invariant annotations |
| Est. VCs | 17 |
| Test | `formal_hq.py`: push+pop sequence maintains heap property |

### 3.4 pprint → `pp`

| Item | Detail |
|------|--------|
| Functions | `pprint`, `pformat`, `pp`, `saferepr` |
| Deps | `io`, `re` (modelled) + `types` (stub) |
| Contracts | `pformat` ensures result >= 0 (string length) |
| Body proof | Mostly contract-only (recursive formatting) |
| Est. VCs | 6 |

### 3.5 csv → `csvmod`

| Item | Detail |
|------|--------|
| Classes | `DictReader`, `DictWriter`, `Sniffer` |
| Functions | `reader`, `writer` |
| Deps | `io`, `re` (modelled) + `types` (stub) |
| C dep | `_csv` — accelerator; pure fallback in same file |
| Contracts | reader produces lists; writer accepts lists |
| Body proof | Contract-only (C-backed iteration) |
| Est. VCs | 8 |

### 3.6 getopt → `gopt`

| Item | Detail |
|------|--------|
| Functions | `getopt`, `gnu_getopt` |
| Deps | `sys` (modelled) + `gettext` (stub) |
| Contracts | result is (opts_list, remaining_args); raises GetoptError on bad input |
| Body proof | Argument parsing loops — `\trusted` on complex branches |
| Est. VCs | 7 |

**Phase 3 deliverable**: 6 modules + 2 stubs, ~51 VCs.

---

## Phase 4 — After functools (future)

These require `functools` which itself has heavy deps (abc, operator, types, weakref + C).
Plan: model a **minimal functools subset** (just `reduce`, `wraps`, `lru_cache` as stubs),
then unlock the chain.

### 4.1 functools (minimal) → `ftools`

Stub `reduce`, `wraps`, `partial`, `lru_cache` with contracts.
Full body proof is impractical (metaclass machinery).

### 4.2 ipaddress → `ipadr`

Pure integer/bit manipulation (2417 lines, 140 functions).
Key target: `IPv4Address`, `IPv4Network` with subnet membership proofs.
Est. VCs: ~50.

### 4.3 operator → `opmod`

Standard operators as functions (one-liner bodies).
Est. VCs: ~30 (mostly trivial body proofs like `def add(a, b): return a + b`).

### 4.4 fnmatch → `fnm`

Unix filename pattern matching.
Deps: functools (Phase 4.1), itertools (C stub), posixpath (stub from os).
Est. VCs: ~10.

### 4.5 glob → `glb`

Pathname expansion. Depends on fnmatch + os.
Est. VCs: ~12.

**Phase 4 deliverable**: 5 modules, ~102 VCs (mostly after functools minimal lands).

---

## Dependency Graph

```
                    ┌──────────┐
                    │ Phase 1  │  (zero deps)
                    │ colorsys │
                    │ html     │
                    │ textwrap │
                    │ string   │
                    └──────────┘

                    ┌──────────┐
                    │ Phase 2  │  (C stubs only)
                    │ signal   │
                    │ struct   │
                    │ linecache│
                    └──────────┘

        ┌─────────────────────────────────┐
        │         Phase 3 stubs           │
        │  types_stub    gettext_stub     │
        └───────┬───────────────┬─────────┘
                │               │
        ┌───────▼──┐    ┌──────▼───┐
        │   abc    │    │  getopt  │
        └───────┬──┘    └──────────┘
                │
        ┌───────▼──┐    ┌──────────┐
        │ numbers  │    │  heapq   │  (independent)
        └──────────┘    └──────────┘
                         ┌──────────┐
                         │  pprint  │←── types_stub
                         │  csv     │←── types_stub
                         └──────────┘

        ┌─────────────────────────────────┐
        │         Phase 4                 │
        │  functools (minimal) ──┐        │
        │       │                │        │
        │   operator    ipaddress        │
        │       │                         │
        │   fnmatch ──→ glob             │
        └─────────────────────────────────┘
```

---

## Execution Checklist

### Phase 1 (immediate — no blockers)
- [ ] `pure_lib/csys/__init__.py` + `formal_csys.py`
- [ ] `pure_lib/htmlm/__init__.py` + `formal_htmlm.py`
- [ ] `pure_lib/txtwrp/__init__.py` + `formal_txtwrp.py`
- [ ] `pure_lib/strmod/__init__.py` + `formal_strmod.py`
- [ ] Commit: "Phase 1: body-proven colorsys, html, textwrap, string"

### Phase 2 (immediate — parallel with Phase 1)
- [ ] `pure_lib/sig/__init__.py` + `formal_sig.py`
- [ ] `pure_lib/strct/__init__.py` + `formal_strct.py`
- [ ] `pure_lib/lcache/__init__.py` + `formal_lcache.py`
- [ ] Commit: "Phase 2: contract-only signal, struct, linecache"

### Phase 3 (after Phase 1+2)
- [ ] `pure_lib/types_stub/__init__.py`
- [ ] `pure_lib/gettext_stub/__init__.py`
- [ ] `pure_lib/abcmod/__init__.py` + `formal_abcmod.py`
- [ ] `pure_lib/nums/__init__.py` + `formal_nums.py`
- [ ] `pure_lib/hq/__init__.py` + `formal_hq.py`
- [ ] `pure_lib/pp/__init__.py` + `formal_pp.py`
- [ ] `pure_lib/csvmod/__init__.py` + `formal_csvmod.py`
- [ ] `pure_lib/gopt/__init__.py` + `formal_gopt.py`
- [ ] Commit: "Phase 3: abc, numbers, heapq, pprint, csv, getopt"

### Phase 4 (future — after functools subset)
- [ ] `pure_lib/ftools/__init__.py` (minimal subset)
- [ ] `pure_lib/ipadr/__init__.py` + `formal_ipadr.py`
- [ ] `pure_lib/opmod/__init__.py` + `formal_opmod.py`
- [ ] `pure_lib/fnm/__init__.py` + `formal_fnm.py`
- [ ] `pure_lib/glb/__init__.py` + `formal_glb.py`
- [ ] Commit: "Phase 4: functools subset, ipaddress, operator, fnmatch, glob"

---

## Success Metrics

| Metric | Before | After Phase 1-3 | After Phase 4 |
|--------|--------|-----------------|---------------|
| Modules in pure_lib | 27 | 40 (+13) | 47 (+20) |
| Total proven VCs (body) | 53 | ~90 (+37) | ~190 (+137) |
| Total proven VCs (tests) | 165 | ~230 (+65) | ~330 (+165) |
| Body-proven modules | 12 | 16 (+4) | 19 (+7) |
| Contract-only modules | 15 | 24 (+9) | 28 (+13) |

---

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| heapq loop invariants too complex | Blocks body proof | Fall back to `\trusted` on sift functions |
| Name clashes (operator `add` etc.) | WhyML VC name collision | Prefix with `op_` (e.g. `op_add`) |
| ipaddress bitwise ops not lowered | Blocks VC generation | Use integer arithmetic model instead |
| regex-heavy functions (html.unescape) | Can't lower to WhyML | Mark `\trusted`, prove contract only |
| `types` stub too thin for pprint | Runtime import failure | Add `MappingProxyType` if needed |

---

## Timeline Estimate

| Phase | Calendar | Effort |
|-------|----------|--------|
| Phase 1 | 1 session | ~3 hours |
| Phase 2 | 1 session | ~2 hours |
| Phase 3 | 2 sessions | ~5 hours |
| Phase 4 | 3 sessions | ~8 hours |
| **Total** | **~7 sessions** | **~18 hours** |
