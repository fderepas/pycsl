# strong-base.md — Plan to deliver full-type stdlib coverage

## Problem statement

The 13 formally-verified modules in `pure_lib/` currently implement only
**pure-integer model functions** — scalar abstractions of the documented API.
PyCSL supports lists (`array int`), tuples (indexed records), classes with
invariants, dicts (`map int (option int)`), and quantification over all of
these. There is no reason to restrict implementations to integers.

This plan bridges the gap: every public function documented in
`test-suite/library_reference/*.rst` gets a **full-type implementation** with
a maximally-precise contract, unless blocked by a documented PyCSL tool gap.

---

## Scope: 13 modules, current vs target

| Module | Dir | RST source | Implemented | Documented | Gap |
|--------|-----|-----------|-------------|------------|-----|
| colorsys | `csys` | colorsys.rst | 7 helpers | 6 functions | 6 full conversions (return tuples) |
| heapq | `hq` | heapq.rst | 7 funcs | 13 funcs | 6 (`*_max` variants, `merge`) |
| textwrap | `txtwrp` | textwrap.rst | 5 funcs | 5 funcs + class | `TextWrapper` class |
| struct | `strct` | struct.rst | 5 funcs | 6 funcs + class | `iter_unpack`, `Struct` class |
| csv | `csvmod` | csv.rst | 5 funcs | 7 funcs + 6 classes | most of the API |
| getopt | `gopt` | getopt.rst | 3 model funcs | 2 funcs | `getopt`, `gnu_getopt` (return lists of tuples) |
| pprint | `pp` | pprint.rst | 5 funcs | 6 funcs + class | `pp`, `pprint`, `PrettyPrinter` class |
| signal | `sig` | signal.rst | 4 funcs | 16 funcs + 3 classes | 12 OS-level functions |
| abc | `abcmod` | abc.rst | 4 funcs | 2 classes + 4 decorators + 2 funcs | `ABC`, `ABCMeta`, `register`, `get_cache_token` |
| linecache | `lcache` | linecache.rst | 5 funcs | 4 funcs | ✅ Complete (extra `getlines`) |
| html.parser | `htmlm` | html.parser.rst | 3 funcs | 1 class + 15 methods | `HTMLParser` class |
| string | `strmod` | string.rst | 4 funcs | 2 classes + 1 func | `Formatter`, `Template` classes |
| numbers | `nums` | numbers.rst | 6 funcs | 5 abstract classes | ABC hierarchy |

---

## Principles

1. **Full types** — Use `list` (array int), `tuple` (indexed record),
   `class` with `#@ class invariant`, and `dict` as supported by PyCSL.
   No more reducing everything to `int`.

2. **RST-faithful** — Every `.. function::` and `.. method::` in the RST
   becomes a Python function/method with a contract derived from the English
   description.

3. **Maximally-precise postconditions** — Exact return values, algebraic
   identities, boundary cases, `\forall` for extrema (per SKILL.md §5).

4. **Axiom registry** — Properties beyond SMT use `#@ proof rocq/lean`.

5. **Classes over scalars** — Where the RST documents a class (`TextWrapper`,
   `Struct`, `HTMLParser`, `PrettyPrinter`), implement it as a PyCSL class
   with `#@ class invariant` and method contracts.

6. **Formal tests generalize all parameters** — No concrete values (per SKILL.md §5).

---

## Phase 1: Tuple-returning functions (colorsys, getopt)

### 1.1 colorsys — full conversions returning tuples

The RST documents 6 conversion functions that all return 3-tuples.
PyCSL supports tuple returns (see 0289.py pattern: `-> tuple` with
`\result[0]`, `\result[1]`, `\result[2]` in postconditions).

**Target:** Replace 7 integer helpers with 6 full functions:

```python
#@ requires 0 <= r and r <= 1000
#@ requires 0 <= g and g <= 1000
#@ requires 0 <= b and b <= 1000
#@ ensures \result[0] == (300 * r + 590 * g + 110 * b) // 1000
#@ ensures \result[1] == ...  # I component formula
#@ ensures \result[2] == ...  # Q component formula
#@ assigns \nothing
def rgb_to_yiq(r: int, g: int, b: int) -> tuple:
    ...
```

Note: We model float [0,1] as int [0,1000] (milli-precision).

| Function | Returns | Complexity |
|----------|---------|-----------|
| `rgb_to_yiq` | (y, i, q) | Pure arithmetic |
| `yiq_to_rgb` | (r, g, b) | Pure arithmetic |
| `rgb_to_hls` | (h, l, s) | Conditional (max/min selection) |
| `hls_to_rgb` | (r, g, b) | Conditional (sector arithmetic) |
| `rgb_to_hsv` | (h, s, v) | Conditional |
| `hsv_to_rgb` | (r, g, b) | Conditional (sector arithmetic) |

**Estimated VCs:** ~60 (replaces current 43)

### 1.2 getopt — list-returning functions

The RST documents `getopt(args, shortopts, longopts=[])` returning
`(opts, args)` where `opts` is a list of (option, value) pairs.

Model: `args: list` (array of int-encoded tokens), return `tuple` with
`\result[0]` = number of parsed options, `\result[1]` = remaining arg count.

For full-type: return a `list` of parsed option indices + a `list` of
remaining arguments. Use `\length(\result)` and element contracts.

| Function | Returns | Complexity |
|----------|---------|-----------|
| `getopt` | (list, list) | Loop with option parsing |
| `gnu_getopt` | (list, list) | Loop with permutation |

**Estimated VCs:** ~30

---

## Phase 2: Class-based modules (textwrap, struct, pprint)

### 2.1 textwrap — add TextWrapper class

The module functions `wrap`/`fill`/`shorten` are wrappers around a
`TextWrapper` instance. Implement the class with state:

```python
#@ class invariant self._width > 0
#@ class invariant self._max_lines >= 0
class TextWrapper:
    def __init__(self):
        self._width = 70
        self._max_lines = 0

    #@ requires width > 0
    #@ ensures self._width == width
    #@ assigns self._width
    def set_width(self, width: int) -> None: ...

    #@ requires \length(text) >= 0
    #@ ensures \result >= 0
    #@ ensures self._width > 0 ==> \result * self._width >= \length(text)
    #@ assigns \nothing
    def wrap(self, text: list) -> int: ...
```

Keep existing module-level functions; they delegate to a default instance.

**Estimated VCs:** ~20 new (class) + 29 existing = ~49 total

### 2.2 struct — add Struct class + iter_unpack

```python
#@ class invariant self._size >= 0
class Struct:
    def __init__(self):
        self._size = 0

    #@ ensures \result == self._size
    #@ assigns \nothing
    def size(self) -> int: ...

    # pack/unpack methods delegate to module-level with self._size
```

Add `iter_unpack`: returns count of iterations = `\length(buffer) // self._size`.

**Estimated VCs:** ~15 new

### 2.3 pprint — add PrettyPrinter class + pp/pprint

```python
#@ class invariant self._indent >= 1
#@ class invariant self._width >= 1
#@ class invariant self._depth >= 0
class PrettyPrinter:
    ...
```

Module-level `pp` and `pprint` are thin wrappers writing to output.
Model output as `assigns \nothing` (pure formatting — length contract).

**Estimated VCs:** ~15 new

---

## Phase 3: Heap operations with list state (heapq)

### 3.1 heapq — max variants and merge

The `*_max` functions mirror the min-heap variants. Same contracts with
reversed comparisons. `merge` returns the total length of merged iterables.

For full-type: functions take `heap: list` and use `\length(heap)`,
`heap[0]` (min/max element contract), and `\old(\length(heap))`.

```python
#@ requires \length(heap) > 0
#@ ensures \result == \old(heap[0])
#@ ensures \length(heap) == \old(\length(heap)) - 1
#@ assigns heap[..]
def heappop(heap: list) -> int: ...

#@ requires \length(heap) > 0
#@ ensures \result == \old(heap[0])
#@ ensures \length(heap) == \old(\length(heap))
#@ assigns heap[..]
def heapreplace(heap: list, item: int) -> int: ...
```

| Function | Contract essence |
|----------|-----------------|
| `heapify_max` | `\length` unchanged, max at root |
| `heappush_max` | `\length` grows by 1 |
| `heappop_max` | returns `\old(heap[0])`, `\length` shrinks by 1 |
| `heappushpop_max` | `\length` unchanged |
| `heapreplace_max` | `\length` unchanged, returns old max |
| `merge` | result length = sum of input lengths |

**Estimated VCs:** ~25 new (replaces/extends current 25)

---

## Phase 4: String-model modules (html.parser, string, csv)

These modules are string-heavy. PyCSL does not have a string theory, but
we can model strings as `list` (array of int codepoints) and specify
length/position contracts.

### 4.1 HTMLParser class

Model the parser as a class with position state:

```python
#@ class invariant self._line >= 1
#@ class invariant self._col >= 0
#@ class invariant self._offset >= 0
class HTMLParser:
    def __init__(self): ...

    #@ requires \length(data) >= 0
    #@ ensures self._offset >= \old(self._offset)
    #@ assigns self._offset, self._line, self._col
    def feed(self, data: list) -> None: ...

    #@ ensures \result[0] == self._line
    #@ ensures \result[1] == self._col
    #@ assigns \nothing
    def getpos(self) -> tuple: ...
```

Handler methods (`handle_starttag`, etc.) are callbacks — specify with
`\trusted` (behavior is user-defined).

**Estimated VCs:** ~20

### 4.2 string.Formatter and string.Template

Model `Formatter` as stateless (all methods are pure transforms on
int-encoded format strings). `Template` holds a template array.

```python
class Template:
    #@ class invariant \length(self._template) >= 0
    def __init__(self): ...

    #@ requires \length(self._template) >= 0
    #@ ensures \result >= 0
    #@ assigns \nothing
    def substitute(self, mapping: list) -> int: ...
```

**Estimated VCs:** ~15

### 4.3 csv — reader/writer with state

Model `reader` as iterating over rows (count-based contract).
`writer` accumulates output. `DictReader`/`DictWriter` add field mapping.

```python
#@ class invariant self._field_count >= 0
#@ class invariant self._rows_read >= 0
class CSVReader:
    #@ ensures \result == self._field_count
    #@ ensures self._rows_read == \old(self._rows_read) + 1
    #@ assigns self._rows_read
    def next_row(self) -> int: ...
```

**Estimated VCs:** ~25

---

## Phase 5: OS/signal and ABC hierarchy (limited by design)

### 5.1 signal — OS-level functions

Most signal functions are OS syscall wrappers. They depend on the World
(I/O, process state). Model with `\trusted` stubs for most; prove the
pure subset (`getsignal`, `raise_signal`, `valid_signals_count`).

Additions feasible without World:
- `valid_signals()` → returns a list/count of valid signal numbers
- `strsignal(signum)` → pure lookup (returns signal name length)
- `alarm(time)` → returns previous alarm value (pure state transition)

**Estimated VCs:** ~10 new

### 5.2 abc — ABCMeta and ABC

`ABC` and `ABCMeta` are metaclass machinery. Model as:
- `ABCMeta.register(subclass)` → modifies registry count
- `ABC` → empty base class with invariant
- `get_cache_token()` → returns monotonically increasing counter

```python
#@ class invariant self._registry_size >= 0
class ABCMeta:
    #@ ensures self._registry_size == \old(self._registry_size) + 1
    #@ assigns self._registry_size
    def register(self, subclass: int) -> None: ...
```

**Estimated VCs:** ~10

### 5.3 numbers — abstract class hierarchy

The `numbers` RST defines an abstract tower: `Number > Complex > Real >
Rational > Integral`. These are ABCs with no concrete methods — they
define **interfaces**. Model each level's contract requirements using
PyCSL's mixin/interface pattern.

**Estimated VCs:** ~10 (interface contracts, no bodies)

---

## Phase 6: Formal tests for all new functions

For every function added in Phases 1–5, write a corresponding formal test
in `pure_lib_test/formal_<module>.py` with universally quantified parameters
and maximally-precise postconditions.

**Estimated VCs:** ~120 new formal test VCs

---

## Summary

| Phase | Modules | New functions | Est. new VCs | Blocked by |
|-------|---------|--------------|-------------|-----------|
| 1 | csys, gopt | 8 | ~90 | — |
| 2 | txtwrp, strct, pp | 3 classes + methods | ~50 | — |
| 3 | hq | 6 functions | ~25 | — |
| 4 | htmlm, strmod, csvmod | 3 classes + methods | ~60 | String model (partial) |
| 5 | sig, abcmod, nums | stubs + ABCs | ~30 | World (signal), metaclass |
| 6 | all | formal tests | ~120 | — |
| **Total** | 13 | ~50 new entries | **~375** | |

Combined with existing 203 module VCs + 197 formal test VCs = **~775 total VCs**.

---

## Execution order

1. **Phase 1** first — pure arithmetic, no classes, highest confidence.
2. **Phase 2** next — classes are well-supported (0076.py, 0191.py patterns).
3. **Phase 3** — heap with list mutation, `assigns heap[..]`.
4. **Phase 4** — string-as-array modeling, may hit tool gaps.
5. **Phase 5** — stubs where World/metaclass blocks full proof.
6. **Phase 6** — formal tests after each phase, not at the end.

---

## Success criteria

- Every `.. function::` and `.. method::` in the 13 RST files has a
  corresponding implementation in `pure_lib/` OR a documented tool-gap entry.
- All implementations use appropriate types (list, tuple, class) — not
  integer-only models.
- All VCs pass (`pycsl` returns SUCCESS).
- Formal tests exercise every public function with universal quantification.
- No `\trusted` on any function that can be body-verified.

---

## Non-goals (documented exclusions)

- `merge(*iterables)` in heapq: requires variadic args (not supported).
- `iter_unpack` producing a true iterator: model as count-based.
- `HTMLParser` callback semantics: user-defined handlers stay `\trusted`.
- Signal functions requiring kernel interaction: `\trusted` stubs.
- `csv.Sniffer`: heuristic analysis, not formally specifiable.
