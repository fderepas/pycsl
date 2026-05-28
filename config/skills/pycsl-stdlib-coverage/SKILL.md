---
name: pycsl-stdlib-coverage
description: Documents the three-artefact discipline (calls-english.md, calls-pycsl.md, src/pycsl_lib/) that keeps PyCSL's stdlib API coverage in lockstep with the source code that uses it. Governs the five-step check loop, the discovery tool (bin/stdlib-coverage.py), the trigger criterion (type-level vs call-level exposure), the CPython version-bump workflow, and the self-annotation gate. Use this skill whenever extending the stdlib stub set, reconciling drift detected by --check, adding entries after a refactor exposes a new stdlib API, or bumping the vendored CPython submodule. Cross-references pycsl-exception-model for raises integration and pycsl-ub-catalog §7.4 for the C-extension import boundary.
---

# PyCSL Stdlib Coverage

## Purpose and scope

This skill governs the contract:

> *"For every standard-library API used by `src/pycsl/`, there is a
> matching English description, a PyCSL contract, and a stub file. The
> three are kept in lockstep by a closed five-step check loop, with a
> discovery tool enforcing the mechanical parts."*

The discipline is required because PyCSL aims to *verify its own source
code*. PyCSL cannot prove a function that calls `os.path.join` without
a model of what `os.path.join` returns; that model lives in the stub
files. As the stub library matures, more of `src/pycsl/` becomes
verifiable — the **self-annotation suite** (workplan §9) is the
acceptance criterion that closes the loop.

## Why a separate skill

The stdlib stub library is part of PyCSL's **trusted computing base**.
A wrong contract in `src/pycsl_lib/os/path.py` silently makes proofs
unsound, exactly as a wrong axiom does. Putting the discipline under
its own change-controlled skill matches the gravity of the artefact —
the same treatment `pycsl-exception-model` gets for the implicit
exception trigger table.

---

## The three artefacts

### 1. `calls-english.md`

Plain-English description of each API entry, anchored to the vendored
CPython documentation. One `##` heading per qualified name. Source
citations point to `cpython/Doc/library/<module>.rst` at the submodule
HEAD; the Python version is documented in the file's header banner
once.

### 2. `calls-pycsl.md`

PyCSL contract per entry. The contract is the source of truth for proof
generation; the English in `calls-english.md` is the source of truth
for *what the contract is supposed to mean*. Each entry must include
`#@ raises { ... }` — empty braces when total, populated names when
partial. The `raises` mandatory rule comes from the NoException
workplan §8.3.

### 3. `src/pycsl_lib/`

Curated stubs PyCSL's resolver actually reads at import time. Layout
mirrors CPython (`os/path.py`, `re.py`, `json/__init__.py`, ...).
Bodies are `...` or `pass` only — never `return 0`, never real
implementations. A `src/pycsl_lib/MANIFEST.toml` enumerates every stub,
every public symbol, the Python version targeted, and a content hash
for CI drift detection.

**Pre-rename path.** The directory was named `data/lib_stubs/` before
StdlibCoverage workplan PR 3. References in older skills and docs may
still mention the old path; treat them as historical.

---

## The five-step check loop

The loop is implemented by `bin/stdlib-coverage.py`. Steps 1, 2, 4 are
tool-enforceable; step 3 is human/agent review; step 5 is the
self-annotation suite.

### Step 1 — Discovery

```bash
bin/stdlib-coverage.py --discover
```

Walks `src/pycsl/*.py` (recursive) for AST evidence of stdlib usage.
Output is `stdlib-coverage-report.toml` at the repo root — checked
into the repo on every relevant commit so the snapshot is stable. CI
re-runs and compares against the snapshot via `--diff`.

### Step 2 — `calls-english.md` completeness

```bash
bin/stdlib-coverage.py --check english
```

Every entry in the report must have a matching `## <name>` heading in
`calls-english.md`. Fails CI on missing entries.

### Step 3 — `calls-english.md` ↔ `calls-pycsl.md` correspondence

```bash
bin/stdlib-coverage.py --check pycsl
```

Mechanical check — heading correspondence only. The faithfulness
review (English matches contract semantics) is a soft gate, optionally
implemented as an LLM-judge weekly cron (workplan §6, PR 11).

### Step 4 — Stubs match contracts

```bash
bin/stdlib-coverage.py --check stubs            # warning (default)
bin/stdlib-coverage.py --check stubs --strict-stubs   # error
```

Every entry in `calls-pycsl.md` must have a stub in `src/pycsl_lib/`,
and the stub's `#@` contract must be byte-identical (modulo
whitespace) to the contract block in `calls-pycsl.md`. The default
mode is warning-only during the scaffold phase; strict mode is the
post-hand-curation gate.

Reverse check: dead stubs (defined but no longer used by `src/pycsl/`)
are flagged as warnings. Three releases of dead-stub status promotes
to error.

### Step 5 — Self-annotation gate

```bash
bin/run-self-annotation-suite.sh
```

A designated set of `src/pycsl/` modules — initially `errors.py`,
growing over time — is annotated with `#@` contracts and verified by
PyCSL itself. This is the final acceptance criterion: the stubs are
useful iff this suite proves.

Adding a module to the suite is a deliberate act, not automatic. Each
addition validates that the per-PR stub additions are sufficient for
the module's surface.

---

## The trigger criterion (`Formatter`, generalized)

A stdlib symbol `S` needs a stub if either:

- **Type-level exposure.** `S` appears in a function signature of
  `src/pycsl/`: parameter type, return type, attribute type, generic
  argument (`List[S]`). Without the stub, type inference at the
  interface boundary breaks.
- **Call-site reasoning.** `S` is called from `src/pycsl/`, and
  verifying the caller requires reasoning about `S`'s effect on its
  arguments or return value.

The discovery tool classifies each entry on both axes
(`type_level: bool`, `call_level: bool`). An entry can be true on
either, both, or neither — bare `import` statements that aren't used
appear with both false and are not stub-required.

The two cases shape the stub content. A class stub (type-level only)
declares fields and method signatures. A function stub (call-level
only) declares the function signature and contract, no class.

---

## CPython version-bump workflow

The vendored CPython submodule lives at `cpython/` at the repo root.
The current pin is **`3.16-alpha` (main branch HEAD)** — risk
documented in workplan §7.3 and in `calls-english.md`'s header. To
re-pin to a stable release (3.12, 3.13, ...):

1. Re-pin the submodule: `cd cpython && git checkout v3.13.x`.
2. Diff the affected `.rst` files in `cpython/Doc/library/` against
   the version banner currently recorded in `calls-english.md`.
3. For each affected entry, update `calls-english.md` if the English
   semantics changed.
4. For each entry whose English changed, decide whether
   `calls-pycsl.md` and `src/pycsl_lib/` need updates (raises set,
   contract postconditions).
5. Re-run the self-annotation suite. Any breakage points either at a
   stub contract that became too weak, or at a PyCSL expressibility
   gap that this version bump revealed.
6. Update the version banner in `calls-english.md` and the
   `python_version` field in `src/pycsl_lib/MANIFEST.toml`.

This workflow is the same shape as the documentation-bump workflow in
the no_exception plan: the artefact moves with the code.

---

## Discovery tool — `bin/stdlib-coverage.py`

Three modes:

| Mode | Purpose |
|---|---|
| `--discover` | Walk `src/pycsl/`, emit `stdlib-coverage-report.toml`. |
| `--check {english\|pycsl\|stubs\|all}` | Reconcile the report against the artefacts. Exit 1 on drift (stubs are warning-only without `--strict-stubs`). |
| `--diff [baseline]` | Show added/removed entries vs a baseline TOML. |
| `--scaffold {english\|pycsl}` | Emit a per-symbol skeleton with `TODO` placeholders. Used once at workplan setup to seed the initial format. |
| `--manifest` | Generate `src/pycsl_lib/MANIFEST.toml` from on-disk stubs. |

Limits of static analysis (workplan §4.3):

- **Dynamic dispatch is invisible.** `getattr(os.path, name)` cannot
  be resolved. The walker emits a "dynamic stdlib access" warning per
  such site and the developer is expected to either annotate the
  receiver or wrap the call behind a `#@ \trusted` boundary.
- **Untyped methods are fuzzy.** `x.split()` where `x: Any` cannot be
  attributed to `str.split` vs `bytes.split`. The walker emits an
  informational warning; strengthening type annotations in
  `src/pycsl/` reduces the noise.

---

## Interaction with `no_exception`

Every stub in `src/pycsl_lib/` declares `raises { ... }`:

- `dict.__getitem__` → `raises { KeyError }`
- `list.__getitem__` → `raises { IndexError }`
- `int(str)` → `raises { ValueError }`
- `os.path.exists` → `raises { }` (modeled as total)
- `open(path)` → `raises { OSError }`

Callers in `src/pycsl/` that want `no_exception` discharge their
obligations via the existing inter-procedural propagation (NoException
PR 4): a callee's `no_exception E` proof or `raises { E -> P }` clause
flows through the call site automatically.

The `raises` integration is what makes the stub library compound with
the no_exception feature — as the stub set matures, more of
`src/pycsl/` becomes annotatable with `no_exception` claims that
actually discharge.

---

## Interaction with UB-7.4 (C-extension boundary)

`src/pycsl/import_classifier.py` classifies imports against the
deny-list (`ctypes`, `cffi`, `numpy.ctypeslib`, `cython`) and the
trusted-stub set (the contents of `src/pycsl_lib/`). The two
concerns are complementary:

- **Stdlib coverage** is about which stdlib calls have models.
- **UB-7.4** is about which non-stdlib calls are excluded from
  verification.

A future PR may unify the two checks: every import is either covered
by `src/pycsl_lib/`, on the deny-list (rejected unless `\trusted`),
or in the residual `UNRESOLVED` bucket (silently treated as
out-of-scope). The current implementation handles each independently.

---

## Self-annotation: the north star

Stdlib coverage is **finite** — bounded by `src/pycsl/`'s current
surface, estimated at ~5–6 weeks of dedicated effort. Self-annotation
of the full `src/pycsl/` is a **multi-year program** of which this
workplan is the foundation. The distinction must be communicated
clearly:

- "Stdlib coverage complete" = the discovery tool reports zero gaps for
  the current API surface (workplan §9.4).
- "Self-annotation complete" = every module in `src/pycsl/` is in the
  proven suite (workplan §9.2–§9.3 catalog of tractability).

Module-by-module growth criteria for the suite:

| Module | Status | Blocker |
|---|---|---|
| `src/pycsl/errors.py` | ✅ in suite | — |
| `src/pycsl/ir_schema.py` | pending | needs richer `isinstance`/dict-membership stubs |
| `Module4_SemanticAnalyzer.py` (parts) | longer-term | needs visitor-pattern modeling |
| `Module5_IREmitter.py` | longer-term | dispatch tables tractable; recursive emission is harder |
| `Module1_Ingestor.py` | research project | requires modeling libcst |
| `Module2_Parser.py` | research project | requires modeling Lark |
| `Module3_Weaver.py` | research project | in-place AST mutation frame conditions |
| `Module6_WhyMLTranspiler.py` + mixins | research project | recursive string-building dispatch |

---

## Anti-patterns

- **Treating `src/pycsl_lib/` as documentation.** It is read by PyCSL's
  resolver. A wrong contract silently makes proofs unsound. CCB
  process applies to every contract change.
- **Confusing "stdlib coverage" with "self-annotation".** The first is
  finite. The second is open-ended.
- **Inlining stub bodies.** Bodies end with `...` or `pass`. Never
  `return 0` (the pre-rename stubs had this; PR 6 of the workplan
  fixes them).
- **Over-modeling stdlib semantics.** Encode only what `src/pycsl/`
  actually relies on. Anything beyond is YAGNI and increases TCB
  surface.
- **Skipping `raises` clauses.** Mandatory in the entry template,
  empty braces when total.
- **Vendoring CPython docs ad-hoc.** Pin a version, vendor as a
  submodule, document the version once in `calls-english.md`'s
  header.
- **Hand-maintaining `stdlib-coverage-report.toml`.** Regenerated by
  the tool. If contributors are editing it, the tool is wrong or the
  workflow is wrong.

---

## Test-corpus cross-references

Per-stub corpus under `test-suite/corpus/python-reference/stdlib/`,
mirroring `src/pycsl_lib/` layout. Initial seeds (workplan PR 8):

| Subdirectory | Coverage |
|---|---|
| `builtins/` | `len`, `range`, `abs` |
| `os_path/` | `exists` |
| `re/` | `compile` |
| `json/` | `dumps` |
| `collections/` | `Counter` |
| `str_methods/` | `split` |
| `typing/` | `List` |

Self-annotation suite under `bin/run-self-annotation-suite.sh`.
Initial entry: `src/pycsl/errors.py`.

---

## Related skills and docs

- `config/skills/pycsl-exception-model/SKILL.md` — the `raises`
  integration this skill cross-references.
- `config/skills/pycsl-ub-catalog/SKILL.md` §7.4 — the C-extension
  import boundary that complements stdlib coverage.
- `config/skills/pycsl-software-architecture/SKILL.md` Section 1 —
  the directory layout that places `src/pycsl_lib/` next to `src/pycsl/`.
- `docs/pycsl-static-semantics-reference.md` — notes that
  `src/pycsl_lib/` is part of the TCB.
- `docs/pycsl-translational-reference.md` — notes the resolver step
  that maps `from os.path import join` to
  `src/pycsl_lib/os/path.py:join`.
- `StdlibCoverage_Workplan.md` — the foundational workplan.
- `.claude/plans/stdlib-coverage-plan.md` — the PR-by-PR
  implementation plan.
