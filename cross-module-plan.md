# Plan: cross-module contract propagation (bucket-D cluster, 0056–0065 / 0168–0187)

## Context — the surprising finding

The 27 bucket-D failures were assumed to be a **contract-propagation gap** (an imported callee's
`ensures` not reaching the caller, so SMT reports `Unknown (sat)`). Investigation shows that is
**not** the cause:

- **Contract propagation already works.** Spike: a caller importing a *contracted* function from an
  existing module emits the callee as `val double_int (x:int):int ensures { result = 2*x }` into
  the caller's WhyML, and the caller's `ensures \result == 2*x` **discharges**. Verified end-to-end.
- **The `--deep` transitive + circular-detection machinery already exists** (pycsl.py:129–173 —
  `deep=True` recurses into a dependency's own imports; line 141 detects an import cycle and
  stubs the circular part).
- **Real root cause: the imported modules are MISSING.** The 27 tests import from
  `multi_file_lib.{arith, rel_helper, deep_mid, circ_a}` (and `circ_b`), but only
  `base_counter`/`base_store`/`visitor_base` exist in the corpus. `arith.py` was **never
  git-tracked**. So every `double_int`/`triple_int`/… import resolves to an opaque, contract-less
  `val foo_N (x:int):int`, and the caller's postcondition cannot be discharged.

**So this is a corpus-completeness fix — restore the 5 missing fixture modules — with NO
source-code change.** (Contract propagation, aliasing, wildcard, relative, `--deep` transitive,
and circular detection all already work.)

## Fix — add 5 fixture modules under `test-suite/corpus/pycsl-reference/multi_file_lib/`

Contracts derived from each caller's `ensures` (and confirmed against the tests' `__main__`
asserts, e.g. `foobar(5)==10`):

| Module | Function (contract) | Notes |
|---|---|---|
| `arith.py` | `double_int(x)` ⊨ `\result == 2*x`; `triple_int(x)` ⊨ `\result == 3*x` | the workhorse (most tests) |
| `rel_helper.py` | `inc(x)` ⊨ `\result == x + 1` | relative-import fixture (0061/0178/0179) |
| `deep_mid.py` | `double_plus_one(x)` ⊨ `\result == 2*x + 1` | imports `arith.double_int` → **transitive** chain (`--deep`, 0064/0184/0185) |
| `circ_a.py` | `func_a(x)` ⊨ `\result == x + 2`, calls `func_b` | imports `circ_b.func_b` |
| `circ_b.py` | `func_b(x)` ⊨ `\result == x + 1` | imports `circ_a.func_a` → establishes the **cycle** (`--deep`, 0065/0186/0187) |

Each is a normal contracted PyCSL module (`#@ ensures …`, body-verified, no `\trusted`). The exact
five files have already been authored and verified in the working tree (see below).

## Verification — already done in the spike

All **27/27** bucket-D tests now PASS with the fixtures present, across every import feature they
exercise:
- basic (`from m import f`) — 0056; multiple names — 0057; module+alias — 0059/0060/0174–0177;
  wildcard (`import *`) — 0063/0182/0183; relative (`from .m import f`) — 0061/0178/0179;
  `--deep` transitive — 0064/0184/0185; `--deep` circular — 0065/0186/0187.

**Remaining step:** run the full corpus sweep (`/tmp/proof_sweep.sh` pattern) to confirm the 27
leave the regression set and nothing else moves — expected post-state: the persistent regression
set shrinks from 28 to **just 0199** (the lone dict-`\length` type error). Adding fixture modules
is purely additive to the corpus; non-multi-file emission is unchanged.

## Out of scope

- **0199** — a `dict`-typed param used with `\length` produces a Why3 `map`-vs-`array` type error.
  Unrelated to imports; it should either get dict-length support or be re-marked
  `# pycsl-expected: FAIL` (it exercises an unsupported shape). Separate, one-file follow-up.
- No change to the import resolver, the propagation path, or `--deep` — they work as-is.

## Critical files

- **New (the entire fix):** `test-suite/corpus/pycsl-reference/multi_file_lib/arith.py`,
  `rel_helper.py`, `deep_mid.py`, `circ_a.py`, `circ_b.py`.
- **No source change.** (For reference, the machinery that already works:
  `src/pycsl/pycsl.py` `_resolve_imports`/`_process_dependency`/`_resolve_*_import` ~:129–396 for
  resolution + `--deep` + cycle detection; `module6_whyml/functions.py` emits a resolved import as
  a `val` carrying its `ensures`.)
