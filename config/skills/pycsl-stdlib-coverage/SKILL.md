---
name: pycsl-stdlib-coverage
description: Battle-tested discipline for writing pure-Python standard library implementations that PyCSL can verify. Covers the full workflow from concrete tests through annotations to formal tests, the shared World architecture (one filesystem, one process table, one clock — mirroring the Unix kernel), three-bucket classification (modelled/specified/stubbed), HAPPY confinement for cross-module coherence, and lessons learned from os (98.0% proven), re (16/16 VCs), warnings (18/18 body + 3/3 formal VCs), and json (6/6 formal VCs). Use this skill when adding a new stdlib module to pure_lib/, annotating existing modules, writing formal tests, or diagnosing PyCSL proof failures.
---

# PyCSL Stdlib Coverage

## Purpose and scope

This skill governs the creation and verification of **pure-Python
standard library implementations** that PyCSL can formally verify. The
goal: for every stdlib API that PyCSL uses internally, provide a
verifiable pure-Python model so that PyCSL can eventually verify its
own source code (self-annotation).

The implementations live in `pure_lib/<module>/` with inline PyCSL
contract annotations. They are **real, runnable Python** — not stubs,
not `pass` bodies. This matters: the implementations are tested
concretely *and* proved formally.

### Everything can be made pure-Python

**No module is inherently un-modelable.** Even modules that interact
with hardware, the OS kernel, the network, or the runtime itself can
be made pure-Python by building an **abstract model** of the
underlying resource — exactly as `pure_lib/os/UnixInodeFileSystem.py`
models the Unix inode layer with pure-Python arrays and integers.

The pattern:
1. **Identify the resource** — what external state does the module
   read/write? (filesystem, process table, clock, network, memory)
2. **Model it as a Python class** — represent the resource's state as
   fields (lists, dicts, ints). Example: `UnixInodeFileSystem` uses
   arrays for inodes, data blocks, and a free-block bitmap.
3. **Implement APIs against the model** — each stdlib function becomes
   a method that operates on the model's fields, with full contracts.
4. **Prove properties of the model** — because the model is pure
   Python with integer/array operations, PyCSL can verify it.

The model does NOT need to be a perfect replica of the real
implementation. It needs to faithfully capture the **contract-relevant
behavior**: pre/postconditions, state transitions, error conditions.
Abstract away implementation details (caching, buffering, OS-specific
paths) that don't affect the functional contract.

See `making-it-pure-5.md` for the definitive plan.

---

## Source of truth — what shapes every stub

A `pure_lib/` module is not invented; it is **transcribed from Python's
sources of truth**. Two axes decide what a stub must say and do (see
`csl-philosophy` "The source of truth" for the family-wide statement):

- **English — the normative specification.** What the API is *specified*
  to do, including its error conditions:
  - the [Python language reference](https://docs.python.org/3/reference/index.html)
    (semantics of the constructs the module uses), and
  - the [standard library reference](https://docs.python.org/3/library/index.html)
    (the documented behavior of the module itself).
  Mirrored locally under `test-suite/library_reference/`. **This is the
  source of the contracts** — every `ensures` should be a formal shadow
  of a sentence in the library reference (see "Contracts must reflect the
  English specification" below).
- **Execution — the reference implementation.** What the API *actually
  does*: [CPython](https://github.com/python/cpython). It is the ground
  truth for everything the English leaves implementation-defined or
  silent — exact exception types (`KeyError` vs `IndexError`), boundary
  results, iteration/insertion order, what `None`/empty inputs yield.
  **The runnable pure-Python model must agree with CPython** on every
  input the concrete tests exercise.

**How they divide the work on a stub:**
1. Read the **library reference** entry → write the strongest contract it
   justifies (intended behavior, documented exceptions).
2. Where the reference is silent or ambiguous → consult **CPython** for
   the actual behavior, and model *that* (do not guess a convenient
   answer). Pin it with a concrete test against real CPython.
3. Where the reference and CPython **disagree** → that is a finding to
   surface (a doc bug or a CPython quirk), not a coin to flip — record
   the decision and which source you followed, in the module's notes.

This is the **Squeeze Strategy's cornerstone (S0), and the first step of
Extreme Rigor.** A stub is *squeezed* between the two sources of truth:
the library reference bounds its contract from above (the strongest
postcondition the English justifies), CPython bounds it from below (what
actually executes). **Squeezed between the two, the stub has no freedom**
— there is no convenient contract to choose, only the one both force.
That squeeze is *why* a faithful stdlib is even possible: you are not
designing behavior, you are transcribing it. Do this **first**, before
loop invariants or any `\trusted` decision (`csl-from-scratch` §1.5 habit
0; `csl-philosophy` "The source of truth"). The three-bucket
classification, the exception model, and the no-more-int typing all exist
to keep the model honest to these sources.

---

## The World: a shared pure-Python kernel

The Unix kernel maintains **one** coherent state. Our models mirror
that: a single `World` object shared by reference across all modules.
Private copies would let you prove false cross-module theorems.

### World structure

```python
class World:
    clock: ClockModel             # monotonic ticks (Unix §8.4)
    fs: UnixInodeFileSystem       # inodes, data, bitmaps, FDs (Unix §3-§5)
    proc: ProcessState            # pid, cwd, argv, env, umask (Unix §6, §7.2)
```

### Region-partitioned ownership

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

### Coherence via HAPPY confinement

Cross-module preservation is achieved by **confinement, not per-call
`assigns`**. A HAPPY (High-level Assertion-Producing PYthon
requirement) declares one integrity property per World subsystem:

```python
#@ happy fs_ownership:
#@     protects world.fs.disk, world.fs.inodes, world.fs.bitmaps, world.fs.fd_table
#@     writes outside owner set forbidden
#@     except <fs methods: sys_open, sys_write, _write_inode, ...>

#@ happy proc_ownership:
#@     protects world.proc.cwd_inode, world.proc.environ, world.proc.argv, ...
#@     writes outside owner set forbidden
#@     except <proc methods: chdir, setenv, ...>

#@ happy clock_ownership:
#@     protects world.clock._ticks
#@     writes outside owner set forbidden
#@     except monotonic
```

**What this buys:** because `sys`, `io`, `time`, `subprocess`, and
the pure modules have **no direct write sites** into `world.fs.*`
(all their fs mutation routes through fs methods), the ownership
checks confirm they cannot perturb the fs region. Therefore **any fs
file is preserved across a sys/time/io call with no `assigns` clause
at all** — preservation is a corollary of the ownership invariant.

### Flush-through I/O model

`io.StreamModel.write` routes directly to `world.fs.sys_write` with
no private buffer. This means:
- After `io.write(data)`, `os.read(same_fd, n)` sees `data`
- No buffer↔inode divergence — no aliasing problem
- The only fs write site is inside fs (covered by `fs_ownership`)

### Three-bucket classification

Every symbol falls into exactly one bucket:

| Bucket | Meaning | VC value |
|--------|---------|----------|
| **Modelled** | Pure-Python stand-in preserving real semantics | A real proof |
| **Specified** | Axiomatized contract you trust (enters the TCB) | Sound only for stated properties |
| **Stubbed** | Signature only, no semantics | Proves nothing |

Coverage is **always reported per bucket**. A 100%-specified module
can show "100% proven" while guaranteeing nothing. The headline
"os: 98% of 4101 VCs" is meaningful because those are modelled-bucket
VCs — real proofs of real code.

### Module-by-module bucketing

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

### Soundness Ledger (TCB)

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

### Implementation order (phased)

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

```
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
pure_lib_test/
  0001.py                    # Concrete test: os write/read round-trip
  0002.py                    # Concrete test: re matchers (10 tests)
  0003.py                    # Concrete test: warnings (5 tests)
  0004.py                    # Concrete test: json (15 tests)
  formal_0001.py             # Formal test: os (18/18 VCs)
  formal_0002.py             # Formal test: re (16/16 VCs)
  formal_0003.py             # Formal test: warnings (3/3 VCs)
  formal_0004.py             # Formal test: json (6/6 VCs)
lib/
  calling.json               # Call graph: which stdlib symbols to cover
```

### Two repos

- **`pycsl_copy/pycsl`** — the modules being verified (pure_lib, tests)
- **`pycsl`** — the PyCSL tool itself (src/pycsl/)

### Two verification levels

1. **Body-level** — PyCSL verifies the function implementation directly.
   Works best for integer-heavy code (os filesystem, warnings). Requires
   the full function body to compile to valid WhyML.

2. **Stub-level** — PyCSL generates `val` declarations (abstract
   function specs) from `__init__.py` imports. Formal tests verify
   properties through these stubs. Works for string-heavy code (re)
   or partially-verifiable modules (json) where body-level verification
   hits tool gaps.

3. **Thin API wrapper** (new pattern from json) — When most of a module
   fails body-level proof, create a `_api.py` with:
   - Body-verified functions for simple logic (integer ops only)
   - Stub wrappers that delegate to the real implementation for complex code
   - This gives you *some* body-level proof without fighting the tool

---

## The workflow (battle-tested)

### Step 1 — Write a concrete test

Create `pure_lib_test/NNNN.py` that imports from `pure_lib/<module>`
and tests all key functions with concrete values. Run it:

```bash
python3 pure_lib_test/0002.py
# PASS: 1 — whitespace matcher
# ...
# PASS: 10 — flags have correct values
```

### Step 2 — Annotate the implementation

Add `#@ requires`, `#@ ensures`, `#@ assigns` annotations inline.
Focus on:
- **Preconditions**: input bounds (`pos >= 0`)
- **Postconditions**: return ranges (`\result >= 0 or \result == -1`)
- **Frame conditions**: `assigns \nothing` when pure
- **Class invariants**: field relationships (`self._end >= self._start`)
- **Loop invariants**: needed for while loops in proofs

### Step 3 — Generate WhyML and iterate

```bash
cd /path/to/pycsl
PYTHONHASHSEED=0 PYTHONPATH=src:src/pycsl .venv/bin/python -c "
import sys
sys.argv = ['pycsl', '--keep-mlw', '--no-proof', '../pycsl_copy/pycsl/pure_lib/re/__init__.py']
from pycsl.pycsl import main
main()
"
```

Check the `.mlw` file. Fix naming issues, type mismatches, missing
imports. Iterate until WhyML type-checks.

### Step 4 — Run body-level proof (if feasible)

```bash
# Remove --no-proof to run the full proof
sys.argv = ['pycsl', '--keep-mlw', 'pure_lib/os/__init__.py']
```

For integer-heavy code (os), this works well — 98.0% proven.
For string-heavy code (re), body-level proof is blocked by tool gaps
(see §Tool Gaps below). Proceed to step 5 regardless.

### Step 5 — Write a formal test

Create `pure_lib_test/formal_<module>.py` with **universally quantified
parameters** — every parameter must be symbolic, never concrete. The
purpose of a formal test is to prove that a property holds **for all
valid inputs**, not just one specific test case.

**Critical rule: generalize ALL parameters.**

A formal test that uses concrete values is *not* a formal test — it is
just a concrete test re-stated in PyCSL syntax. Compare:

```python
# BAD: concrete test disguised as formal test — proves nothing new
#@ ensures \result == 12
def test_gcd_zero_right() -> int:
    return gcd(12, 0)

# GOOD: universally quantified — proves gcd(n, 0) == n for ALL n
#@ requires n >= 0
#@ requires n < 2147483647
#@ ensures \result == n
def test_gcd_zero_right(n: int) -> int:
    return gcd(n, 0)
```

Each test function:
- Takes **symbolic parameters** with `requires` matching the callee's
  preconditions (plus overflow guards like `< 2147483647` when needed)
- Has an `ensures` clause that is provable solely from the callee's
  postconditions applied to the symbolic arguments
- Returns an expression whose value the `ensures` clause constrains

The prover must discharge the `ensures` for **every** integer satisfying
the `requires`. This is universal quantification — the essence of formal
verification.

See `docs/glossary/formal-test.md` for the concept.

### Contracts must reflect the English specification

When writing postconditions, **always derive them from the English
documentation in `test-suite/library_reference/`**, not from what
seems "minimal" or "safe" to assert. A contract like
`ensures text == 0 -> \result == 0` (wrapping empty text yields an
empty list) is not "leaking implementation details" — it is a direct
transcription of the documented behavior: *"Returns a list of output
lines"*, and an empty input trivially produces an empty list.

Weakening a postcondition to merely `ensures \result >= 0` when the
English spec says something stronger produces a model that is
technically provable but **unfaithful to the library semantics**.
The whole point of formal verification is to capture *intended
behavior*, not to minimize proof obligations. The RST documentation
is the ground truth; the contract is its formal shadow.

**Rule**: read the English description first, write the strongest
postcondition it justifies, then verify the body satisfies it.
Only weaken if the English is genuinely ambiguous.

### Always maximise postcondition precision

After writing a contract, **always ask: can I make the postcondition
more strict?** A loose postcondition like `ensures \result >= 0` is
technically true but vacuous — it tells the caller almost nothing.
The goal is to capture the **mathematical essence** of the function.

Example — `gcd(a, b)`:

```python
# BAD: technically true, but says almost nothing
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def gcd(a: int, b: int) -> int: ...

# GOOD: captures what gcd IS
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ ensures (a > 0 or b > 0) ==> \result > 0
#@ ensures (a > 0 or b > 0) ==> a % \result == 0
#@ ensures (a > 0 or b > 0) ==> b % \result == 0
#@ ensures (a > 0 or b > 0) ==>
#@   (\forall k; (k > 0 and a % k == 0 and b % k == 0) ==> k <= \result)
#@ assigns \nothing
def gcd(a: int, b: int) -> int: ...
```

The `\forall k` clause says: no common divisor is larger than the
result. Together with `a % \result == 0 and b % \result == 0`, this
*defines* gcd — the greatest common divisor. A caller can now reason
algebraically about the result, not merely know it is non-negative.

**Checklist for every postcondition:**
1. Does it capture the *exact* return value when possible? (`== f(args)`)
2. Does it capture the *divisibility*, *monotonicity*, or *algebraic
   identity* the function computes?
3. Does it state the *boundary/edge-case* behavior? (e.g., `a == 0 ==> \result == b`)
4. Does it use `\forall` to express *maximality* or *minimality* when
   the function computes an extremum (gcd, max, min, lcm)?
5. Can a caller prove **more** about their own code using this contract?
   If not, the contract is too weak.

### Step 5b — Use the axiom registry for inductive properties

SMT solvers cannot discharge properties that require induction,
cross-function relational reasoning, or uninterpreted predicates.
For these, import cross-validated axioms from the **axiom registry**
(`_AXIOM_REGISTRY` in `src/pycsl/module6_whyml/preamble.py`).

**Syntax:**
```python
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_step
```
Each `#@ proof` directive emits a WhyML `axiom` in the preamble.
Always cite both Rocq and Lean (cross-validation is required).

**Available axiom families:**

| Prefix | Axioms | Use case |
|--------|--------|----------|
| `Pycsl.Reference.Gcd.*` | 7 (gcd_0, gcd_step, gcd_divides_a/b, gcd_greatest, gcd_result_nonneg/positive) | Euclidean GCD: loop invariant `gcd(x,y)==gcd(a,b)`, divisibility, maximality |
| `Pycsl.Reference.Perm.*` | 2 (permut_refl, rev_permutation) | Permutation properties over `array int` — uninterpreted `permut` predicate |
| `Pycsl.Reference.Json.*` | 1 (mirror_involution) | Inductive properties over recursive `#@ datatype` — structural induction |
| `UnixFs.Bitmap.*` | 1 (bit_and_one_in_zero_one) | Bitwise `(x >> y) & 1 ∈ {0,1}` — Z3 blowup avoidance |
| `UnixFs.Struct.*` | 3 (i1a1, i2, i18 round_trips) | `struct.pack`/`struct.unpack` round-trip identity |

**When to use:**
- Loop invariants with `gcd(x,y) == gcd(a,b)` preservation — needs `gcd_step`
- `\forall k` maximality in GCD postcondition — needs `gcd_greatest`
- `\permutation` on reversed/sorted arrays — needs `rev_permutation`
- Inductive properties over recursive datatypes — needs structural-induction lemma
- Any VC where Alt-Ergo/Z3 returns Timeout or Unknown after 60 s

**Pattern (GCD flagship, from `test-suite/corpus/pycsl-reference/0342.py`):**
```python
#@ proof rocq Pycsl.Reference.Gcd.gcd_0
#@ proof lean Pycsl.Reference.Gcd.gcd_0
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_step
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_a
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_a
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_b
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_b
#@ proof rocq Pycsl.Reference.Gcd.gcd_greatest
#@ proof lean Pycsl.Reference.Gcd.gcd_greatest
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof lean Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_positive
#@ proof lean Pycsl.Reference.Gcd.gcd_result_positive
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == gcd(a, b)
#@ ensures \result >= 0
#@ ensures (a > 0 or b > 0) ==> \result > 0
#@ ensures (a > 0 or b > 0) ==> a % \result == 0
#@ ensures (a > 0 or b > 0) ==> b % \result == 0
#@ ensures (a > 0 or b > 0) ==>
#@   (\forall k; (k > 0 and a % k == 0 and b % k == 0) ==> k <= \result)
#@ assigns \nothing
def gcd(a: int, b: int) -> int:
    x: int = a
    y: int = b
    #@ loop invariant x >= 0 and y >= 0
    #@ loop invariant gcd(x, y) == gcd(a, b)
    #@ loop variant y
    while y != 0:
        r: int = x % y
        x = y
        y = r
    return x
```

**Trust model:** Each axiom qualname maps to paired Rocq + Lean proofs
in `NNNN.proofs/{rocq,lean}/`. The `audit_proof.py` tool verifies that
both proof assistants accept the lemma and that neither introduces
extraneous axioms beyond the kernel allowlist. A missing or failing
cross-check is a hard error.

### Step 6 — Document tool gaps

Any PyCSL limitation discovered during steps 3–5 goes into a
requirements document (`NNNN.md` at repo root):
- `1009.md`: R1–R4 (stub generation, tuple results, assigns)
- `1111.md`: R5–R7 (str params, constant values, default args)
- `07-0647-gaps.md`: R8–R13 (keyword clashes, string ops, class returns)

---

## Current status

### os module — 98.0% proven (body-level)

| Metric | Value |
|--------|-------|
| Valid VCs | 4019 |
| Total VCs | 4101 |
| Proven rate | 98.0% |
| Unproven goals | 41 |
| Formal test | 18/18 VCs ✅ |

The 41 remaining failures trace to `subscript_get` abstraction — when
inlined code reads `inode[2]` on a record field, PyCSL emits
`subscript_get !inode 2` (abstract) instead of `!inode[2]` (array
access). This is a PyCSL tool gap, not a pure_lib issue.

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

## Lessons learned

### Naming: Why3 keyword and symbol clashes

PyCSL lowercases Python class names to form Why3 types. Several
Python names collide with Why3 keywords or with PyCSL's own emitted
symbols:

| Python name | Clash | Fix |
|-------------|-------|-----|
| `Match` | `match` is a Why3 keyword | Rename to `ReMatch` |
| `Pattern` | `isinstance` emits `val constant pattern` colliding with `type pattern` | Rename to `RePattern` |
| `compile(pattern, ...)` | Parameter `pattern` collides with type `pattern` | Rename parameter to `pat_src` |

**Rule:** Always check generated `.mlw` for name collisions after
adding a new class. Keep Python API compatibility via `__init__.py`
re-exports (`ReMatch as Match`).

### Naming: Python stdlib module name clashes

PyCSL's import resolver can pick up the *real* stdlib module instead
of your `pure_lib/` version if names collide:

| Module name | Clash | Fix |
|-------------|-------|-----|
| `warnings` | Resolves to stdlib `warnings` | Name directory `warn/` |

**Rule:** If your pure_lib module shares a name with a top-level
Python stdlib package, rename it. Use `__init__.py` to re-export
under the expected API names.

### Function contracts don't propagate through re-exports

**Critical architecture decision:** When `__init__.py` does
`from ._core import my_function`, PyCSL generates a stub for
`my_function` but **does NOT carry its `requires`/`ensures` contracts
through**. Only **class** contracts (invariants, method specs) survive
re-export.

**Consequence:** For modules that export top-level functions (not
classes), put the annotated function definitions **directly in
`__init__.py`**, not in a submodule. This is why `pure_lib/warn/`
has everything in `__init__.py`.

### Constants: use literals, not imports

Cross-module constants (e.g., `O_CREAT = UnixInodeFileSystem.O_CREAT`)
become abstract `val constant` with no value in WhyML. PyCSL's
`module_constants` works for the file being verified but NOT for
imported modules.

**Fix:** Define constants as literals directly:
```python
O_RDONLY = 0
O_WRONLY = 1
O_CREAT = 64
```

### String methods: known postconditions

- `.ljust(width)` — has `ensures Array.length result >= x0` ✅
- `.ljust(width, fillchar)` — 2-arg form has type issues (fillchar
  `b'\x00'` becomes `array int`, stub expects `int`) ❌
- `.encode()` — length is genuinely unknown; no useful postcondition
- `.zfill(width)` — has length ensures ✅

### Default arguments and type annotations

- Default arguments: PyCSL generates N-arg stubs; callers must pass
  all args explicitly. `open(filename, O_RDONLY)` not `open(filename)`.
- `filename: str` annotation: causes type mismatch (string → int in
  Why3). Drop the `: str`.

### Inliner limitations

- Module-level helper calls in inlined bodies get replaced with
  `Array.make 1 0` instead of the actual function call.
- **Workaround:** Remove preconditions that depend on helper
  postconditions, or inline the logic directly.
- Method calls on module-level objects may miscount arguments
  (`self` not counted), causing inliner errors.

### Loop patterns: tuple unpacking and chained comparisons

**Tuple unpacking in for-loops is broken.** Code like
`for action, cat in _filters:` generates WhyML where `cat` is
undefined. **Workaround:** Use parallel lists + index-based access:

```python
_filter_actions = []  # list of action strings
_filter_cats = []     # list of category strings
# Access via _filter_actions[i], _filter_cats[i] in a while loop
```

**Chained comparisons are broken.** `0 <= i <= n` lowers to
`((0 <= !i) <= !n)` — applying `<=` to a boolean. **Workaround:**
Split into two separate invariants:

```python
#@ loop invariant 0 <= i
#@ loop invariant i <= n
```

### Exception propagation across functions

PyCSL does not propagate `raises` clauses through callees. If
function `A` calls function `B` which raises `Exception`, `A` does
NOT automatically get a `raises` annotation.

**Consequence:** Functions that call exception-raising helpers can't
be formally tested (the formal test can't declare the exception
possibility). **Workaround:** Either restructure to avoid calling
the exception-raising function, or exclude that function from formal
tests and document why.

### `assigns \nothing` is implicit

In Why3, a `val` without `writes` clause is already effect-free.
You do NOT need to explicitly emit `writes {}`. The `assigns \nothing`
annotation is still useful documentation but doesn't change the proof.

### Tuple result postconditions

`\result[0] >= 0` correctly lowers to
`let (_r0_, _) = result in _r0_ >= 0`. This works since the R3 fix.

### Proof strategy for remaining failures

When body-level proof is stuck:

1. Check if the failure is a **PyCSL tool gap** (subscript_get, string
   ops, etc.) — document in requirements, move on.
2. Check if a **stronger precondition** helps — e.g., adding
   `inode_num < 32` guard made a loop invariant provable.
3. Check if a **weaker postcondition** is still useful — removing
   `\valid(name_bytes, 30)` eliminated downstream failures.
4. Fall back to **stub-level** formal tests through `__init__.py`.

---

## Known PyCSL tool gaps (blocking further progress)

### Critical (blocks body-level proof for most code)

| ID | Gap | Modules affected |
|----|-----|-----------------|
| R13 | Class-returning functions: `int` return type vs record literal | re |
| subscript_get | Array-field reads in inlined code are abstract | os (~70% of failures) |

### High (blocks string-heavy code)

| ID | Gap | Modules affected |
|----|-----|-----------------|
| R10 | Missing `use string.String` for `in` operator | re |
| R11 | `self` parameter missing from method bodies | re |
| R12 | `isdigit()` drops receiver (chained method call) | re |
| — | Inliner method arg count: `self` not counted for module-level objects | json |
| — | Tuple parameter destructuring: `let (a, b) = pair` type mismatch | json |
| — | Pipeline crash (`NoneType.lstrip`) in encoder code | json |

### Medium (blocks specific patterns, workarounds exist)

| ID | Gap | Workaround |
|----|-----|-----------|
| R5 | `filename: str` → WhyML `string` but APIs use `int` | Drop `: str` |
| R6 | Imported constants have no value | Use literal integers |
| R7 | Default arguments not in cross-module stubs | Pass all args explicitly |
| R8 | `match` is Why3 keyword | Rename class |
| R9 | isinstance constant name collision | Rename class |
| — | Tuple unpacking in for-loops (`for a, b in lst:`) | Parallel lists + index loop |
| — | Chained comparisons (`0 <= i <= n`) | Split into two invariants |
| — | `raises` not propagated through callees | Restructure or exclude from formal test |
| — | Stdlib module name clash in import resolver | Rename directory (e.g., `warn/`) |

---

## How to run PyCSL

### Import resolution (critical)

PyCSL resolves imports by searching: (1) the file's directory, (2) CWD,
(3) built-in `Lib/`. This means **CWD controls which `pure_lib/` is
found**.

- The pycsl **tool** repo has its own `pure_lib/` (with `os/`, `re/`,
  `json/` — synced separately).
- New modules (like `warn/`) only exist in `pycsl_copy/pycsl/pure_lib/`.
- **For new modules**: must run from `pycsl_copy/pycsl` as CWD.
- **For established modules** (in both repos): can run from either.

```bash
# For NEW modules not yet in the tool repo:
cd /path/to/pycsl_copy/pycsl
PYTHONHASHSEED=0 PYTHONPATH=/path/to/pycsl/src:/path/to/pycsl/src/pycsl \
/path/to/pycsl/.venv/bin/python -c "
import sys
sys.argv = ['pycsl', '--keep-mlw', 'pure_lib_test/formal_0003.py']
from pycsl.pycsl import main
main()
"
```

```bash
# For modules already in the tool repo:
cd /path/to/pycsl
PYTHONHASHSEED=0 PYTHONPATH=src:src/pycsl .venv/bin/python -c "
import sys
sys.argv = ['pycsl', '--keep-mlw', '../pycsl_copy/pycsl/pure_lib/os/__init__.py']
from pycsl.pycsl import main
main()
"
```

- `--keep-mlw`: preserve generated `.mlw` file for inspection
- `--no-proof`: skip proof, only check WhyML generation
- `PYTHONHASHSEED=0`: required for deterministic output
- Provers: Alt-Ergo 2.6.2 (primary), Z3 4.13.3 (fallback)

---

## What to cover next

The `lib/calling.json` file lists all stdlib symbols PyCSL uses.
Modules covered so far: `os`, `re`, `warnings`, `json`. The remaining
23 modules (542 symbols) are planned in `making-it-pure-5.md`.

**Current phase: Foundation (Phase 1).** Build `ClockModel`, wire
fs↔clock, define the `World` aggregate. Then Phase 2 (confinement
HAPPYs) and Phase 3 (quick wins: bisect, keyword, enum, etc.).

**The gate (Phase 3.6):** The fine probe — can PyCSL prove that
writing inode A preserves inode B? — decides whether Phase 5
(tempfile, shutil) uses parametric HAPPY or a narrow `assigns`
fallback. This is the make-or-break question; answer it before
building any fs-mutating module.

---

## Anti-patterns

- **Using `\trusted`** — defeats the purpose. If PyCSL can't prove
  something, identify the missing feature precisely and document it.
- **Abstraction over concrete implementations** — pure_lib modules are
  real runnable Python, not stubs. Test them concretely first.
- **Ignoring formal test failures** — a formal test failure means the
  postcondition is wrong or the implementation has a bug. Fix it.
- **Fighting the tool** — if body-level proof is blocked by 5+ tool
  gaps, switch to stub-level formal tests. Document the gaps and
  move on. Consider the thin API wrapper pattern for partial coverage.
- **Forgetting `PYTHONHASHSEED=0`** — results become non-deterministic
  without it. Always set it.
- **Adding `: str` type annotations** — PyCSL maps `str` to Why3
  `string`, but all APIs use `int`. Drop string annotations.
- **Putting functions in a submodule and re-exporting** — function
  contracts don't propagate through `__init__.py` re-exports. Put
  annotated functions directly in `__init__.py` (classes are fine in
  submodules).
- **Running from the wrong CWD** — PyCSL resolves imports from CWD.
  New modules not yet in the tool repo MUST be run from
  `pycsl_copy/pycsl` as working directory.

---

## Related files

- `1009.md` — PyCSL tool requirements R1–R4
- `1111.md` — PyCSL tool requirements R5–R7
- `07-0647-gaps.md` — PyCSL tool requirements R8–R13
- `docs/glossary/formal-test.md` — defines the formal test concept
- `docs/glossary/axiom-registry.md` — defines the axiom registry concept
- `src/pycsl/module6_whyml/preamble.py` — `_AXIOM_REGISTRY` source of truth
- `test-suite/corpus/pycsl-reference/0342.py` — GCD flagship proof (axiom pattern)
- `lib/calling.json` — call graph of stdlib symbols to cover
