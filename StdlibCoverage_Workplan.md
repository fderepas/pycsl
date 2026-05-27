# PyCSL Workplan — Stdlib API coverage for self-annotation

> Plan for systematically covering the Python standard library APIs used by `src/pycsl/` itself, so that PyCSL can eventually verify its own source code. Three artefacts (`calls-english.md`, `calls-pycsl.md`, `Lib/`) maintained by a closed check loop, with tooling to discover gaps and CI to keep them in sync.

---

## 0. Review of the sketch

Before fleshing out the plan, six issues with the sketch as drafted that materially affect the design. Each is addressed in the body below; they are listed up front so the deviations from the original wording are visible.

**0.1 Terminology — "system call" is a misnomer.** A system call (`syscall(2)`) is an OS kernel boundary: `open`, `read`, `write`, `mmap`. What the sketch describes is Python **standard library API coverage** — `os.path.join`, `re.compile`, `list.append`, `str.split`, `dict.get`. The two are different concerns. Anyone with an OS background reading `calls-english.md` and finding `str.split` will be confused. The workplan uses "stdlib API" throughout; `calls-english.md` and `calls-pycsl.md` keep their proposed names (they're short and the audience now knows what they mean) but the documents themselves clarify scope.

**0.2 The check loop is missing step 5.** The sketch trails off at "5/". I propose step 5 is: "Run PyCSL on a designated self-annotation corpus (initially: a small subset of `src/pycsl/` modules) and verify the proof succeeds." Without a closing step, the loop has no acceptance criterion — coverage is infinite, the question is when it's *enough*. The self-annotation pass is what makes "enough" measurable.

**0.3 The trigger criterion is more subtle than "used".** The `Formatter` example reveals the real rule: a stdlib symbol needs a stub when it appears at an *interface boundary* of `src/pycsl/` code — i.e., it appears in a function signature (parameter type, return type, attribute type), OR it is called and PyCSL needs to reason about the call's effect. These are two distinct cases ("type-level exposure" vs "call-site reasoning") and the stub content differs.

**0.4 The bidirectional check is asymmetric.** The sketch checks: code → english (find missing), english ↔ pycsl (consistency), pycsl → Lib (find missing stubs). It does not check: **Lib → pycsl** (dead stubs) or **Lib → code** (stubs whose contract no longer matches what the code uses). Drift in those directions is just as costly. Step 5 of the loop must include reverse checks.

**0.5 "Read the PyCSL and try to guess the English" doesn't scale.** As a validation method this is fine for spot-checks; as a CI gate it needs a more concrete mechanism. I propose two: (a) for each entry, a worked example in the corpus that exercises the contract, and (b) an LLM-judge round-trip check run periodically, not per-commit.

**0.6 `Lib/` vs the existing `data/lib_stubs/`.** The architecture skill states `data/` contains `lib_stubs/ Python stubs`. The sketch introduces `Lib/`. Either this is a rename, a new directory, or a misalignment. The workplan assumes a deliberate rename to `Lib/` (matching CPython's `Lib/` convention) and includes the migration as part of the first PR. If that's wrong, the workplan needs to be re-anchored on the existing path.

These six points are not blocking — the sketch is implementable as-stated. They are surfaced because addressing them in the workplan now is cheaper than discovering them mid-implementation.

---

## 1. Framing

The goal is **PyCSL self-annotation**: making `src/pycsl/*.py` and `src/pycsl/module6_whyml/*.py` verifiable by PyCSL itself. This is the bootstrap milestone where the compiler proves its own implementation against its own contract language.

Stdlib API coverage is **necessary** for that goal: PyCSL cannot prove a function that calls `os.path.join` if PyCSL has no model of what `os.path.join` returns. Stdlib coverage is also **far from sufficient**: it does not address whether `src/pycsl/` code is *expressible* in the PyCSL subset (libcst trees, Lark parsers, recursive AST visitors with dynamic dispatch — these are the harder problems). The workplan is honest about this: coverage is one prerequisite among several.

The discipline this workplan formalizes — three artefacts kept in lockstep by a closed loop with tooling and CI — is generalizable. Once it exists for the stdlib, the same machinery will eventually be needed for libcst, Lark, and any other external library that crosses a PyCSL interface boundary. Designing for one library now while keeping the second-library case in mind is cheap; retrofitting later is expensive.

The interaction with the just-completed `no_exception` work is direct and constant: every stdlib stub must declare the exceptions its modeled function can raise, and most callers of those stubs will eventually be annotated `no_exception`. The two features compound. See §8.

---

## 2. Scope and definitions

### 2.1 What counts as an "API entry"

An API entry is one of:

- **Module function** — `os.path.join`, `re.compile`, `json.dumps`.
- **Builtin function** — `len`, `range`, `print`, `isinstance`, `min`, `max`, `sum`.
- **Method** — `str.split`, `list.append`, `dict.get`, `set.union`.
- **Class** (as a returned or stored type) — `re.Pattern`, `pathlib.Path`, `io.StringIO`.
- **Class instantiation** — `dict()`, `list()`, `set()`, `defaultdict(list)`.
- **Module attribute** — `sys.argv`, `os.sep`, `string.ascii_letters`.

Not in scope as API entries:
- Operators (`+`, `[]`, `in`) — these are part of the language, modeled in Module 6 directly, not via stubs.
- Statements (`for`, `with`, `assert`) — same.
- Magic methods on user-defined types (`__hash__`, `__eq__`) — these are the user's contract, not stdlib.

### 2.2 The trigger criterion (the `Formatter` example, generalized)

A stdlib symbol `S` needs a stub if either:

- **Type-level exposure** — `S` appears in a function signature of `src/pycsl/`. Parameter types, return types, attribute types, generic arguments (`List[S]`). The `Formatter` example: not currently returned by any `src/pycsl/` function, so no stub. If a future refactor exposes it, the stub becomes required *in that PR*.
- **Call-site reasoning** — `S` is called from `src/pycsl/`, and verifying the caller requires reasoning about `S`'s effect on its arguments or return value.

These cases overlap but are not identical. A stub for `Formatter` (case 1) needs class fields and method contracts. A stub for `os.path.join` (case 2) needs the function signature and contract, no class. The two-case structure is reflected in `Lib/` layout (see §3.3).

### 2.3 What "PyCSL reads from Lib" means concretely

When Module 1 (Ingestor) encounters `from os.path import join`, the resolver does not parse CPython's actual `os/path.py`. It parses `Lib/os/path.py` — PyCSL's curated stub. The stub contains `def join(...) -> str: ...` with `#@` contracts encoding what `os.path.join` is *modeled* to do. PyCSL never executes stdlib code; it only proves against its model of it.

This implies the stub directory is part of PyCSL's **trusted computing base**: a wrong contract in `Lib/os/path.py` makes proofs unsound. The workplan treats `Lib/` with the same gravity as `pycsl-exception-model.skill` — it is under CCB control, every contract change is reviewed.

---

## 3. The three artefacts

### 3.1 `calls-english.md`

Plain English description of each modeled API entry, anchored to upstream CPython docs.

Format per entry:

```markdown
## `os.path.join(path, *paths)`

Joins one or more path components intelligently. The return value is the
concatenation of `path` and any members of `*paths` with exactly one directory
separator following each non-empty part, except the last...

Raises: nothing under normal use; `TypeError` if a component is not str or bytes-like.

Source: cpython/Doc/library/os.path.rst (Python 3.11)
Modeled in: Lib/os/path.py
PyCSL contract: calls-pycsl.md#ospath-join
```

The "Source" line is the audit trail — when CPython docs change, this is the line to grep. The Python version is part of the citation because behavior varies (e.g., `dict` ordering became a language guarantee in 3.7; `dict.popitem` changed semantics).

Granularity rule: one heading per entry. Group related entries (`str.split`, `str.rsplit`, `str.splitlines`) under separate `##` headings, not folded together — search-by-name is the primary access pattern.

### 3.2 `calls-pycsl.md`

PyCSL-contract description of each entry. The contract should be readable as a direct encoding of the English.

Format per entry:

```markdown
## `os.path.join`

```python
#@ requires len(path) >= 0
#@ ensures len(\result) >= len(path)
#@ ensures \result.startswith(path) ==> len(paths) == 0 || ...
#@ raises { TypeError }
#@ no_exception ZeroDivisionError, IndexError, KeyError, ValueError
def join(path: str, *paths: str) -> str: ...
```

The contract is the source of truth for proof generation. The English in
calls-english.md is the source of truth for what the contract is supposed to mean.

Cross-check: read the contract above and rewrite it in English; compare to
calls-english.md. They should agree on observable behavior.
```

The explicit cross-check note at the bottom of each entry institutionalizes the "read the PyCSL and guess the English" validation — it's not a CI step (see §6) but it's the human review discipline.

### 3.3 `Lib/`

Curated stubs that PyCSL's resolver actually reads. Layout mirrors CPython:

```text
Lib/
  os/
    __init__.py        # os.sep, os.path module proxy, os.environ, …
    path.py            # join, exists, split, dirname, basename, …
  string.py            # ascii_letters, digits, … (Formatter NOT here yet)
  re.py                # compile, match, search, … and Pattern class iff exposed
  json/
    __init__.py        # dumps, loads, JSONDecodeError class iff exposed
  collections/
    __init__.py        # OrderedDict, defaultdict, …
  io.py                # StringIO, BytesIO classes iff exposed
  pathlib.py           # Path class iff exposed
  typing.py            # List, Dict, Optional, … (mostly aliases for PyCSL types)
  builtins.py          # len, range, isinstance, … (the special module)
  __init__.py          # version stamp + manifest reference
```

Each `.py` file contains:

- Function stubs with `#@` contracts.
- Class stubs (only when the class appears at a type-level interface in `src/pycsl/`) with field type declarations and method contract stubs.
- Module-level constants (`os.sep`, `sys.platform`) where used.

Stubs **never have function bodies** — they end with `...` or `pass`. PyCSL is reading them for *signatures and contracts only*. The presence of a body would be misleading: PyCSL does not execute or even fully parse it.

A `Lib/MANIFEST.toml` enumerates every stub file, every public symbol in each, the upstream Python version targeted, and a hash of the stub content for CI drift detection.

---

## 4. Tooling — `bin/stdlib-coverage`

Step 1 of the check loop ("list all stdlib API entries used in src/pycsl") is infeasible by hand at any scale beyond a few dozen entries. A discovery tool is the first PR.

### 4.1 What it does

A Python AST walker over `src/pycsl/*.py` and `src/pycsl/module6_whyml/*.py` that emits a list of:

- All `Import` and `ImportFrom` names → the set of stdlib modules used.
- All `Attribute` accesses on those modules → the set of called functions and accessed constants.
- All `Call` nodes targeting methods of stdlib types (where determinable) → the set of methods used.
- All function signatures (parameter type annotations, return type annotations) referencing stdlib types → the set of type-level exposures.

Output: a structured report (`stdlib-coverage-report.toml` or JSON) listing each entry, its source location(s), and whether it appears at type-level, call-level, or both.

### 4.2 Three CI modes

- **`bin/stdlib-coverage --discover`** — produces the full report from scratch, regenerating from src/pycsl.
- **`bin/stdlib-coverage --check`** — compares the report against `calls-english.md`, `calls-pycsl.md`, and `Lib/MANIFEST.toml`. Fails CI if any entry is in the code but not in all three artefacts, or vice versa.
- **`bin/stdlib-coverage --diff`** — shows the delta against a baseline (e.g., the previous commit's report). Used in PR review to make stdlib-surface changes visible.

The `--check` mode is the CI gate. It is the operationalization of the check loop.

### 4.3 Limits of the AST walker

Dynamic dispatch is invisible to it: `getattr(os.path, name)` cannot be resolved statically. The walker emits a "dynamic stdlib access" warning per such site, and `src/pycsl/` is expected to avoid them (or quarantine them behind `@trusted` boundaries — see UB-7.4 from the previous workplan). Methods on values whose type isn't annotated are also fuzzy: `x.split(...)` where `x: Any` cannot be attributed to `str.split` vs `bytes.split`. Strengthening type annotations in `src/pycsl/` reduces this noise; the workplan accepts residual false negatives as the cost of static-only discovery.

---

## 5. The check loop, fully specified

The five steps run in this order, each gated on the previous. Steps 1, 2, 4 are tool-enforceable; step 3 is human/agent review; step 5 is integration test.

### Step 1 — Discovery

```
bin/stdlib-coverage --discover > stdlib-coverage-report.toml
```

Produces the canonical list. **Output is checked into the repo** so every commit has a stable snapshot. CI re-runs and compares.

### Step 2 — `calls-english.md` completeness

For every entry in the report, `calls-english.md` must have a matching heading. Missing entries are added with English from `cpython/Doc/library/<module>.rst`. The CPython repository must be available as a git submodule or vendored copy at a pinned version (recommend pinning to the same Python version as the project's runtime).

CI check: `bin/stdlib-coverage --check english`. Fails if any entry in the report has no matching heading in `calls-english.md`.

### Step 3 — `calls-english.md` ↔ `calls-pycsl.md` correspondence

Every entry in `calls-english.md` has a matching entry in `calls-pycsl.md`, and the PyCSL contract is a faithful encoding of the English.

CI check (mechanical): `bin/stdlib-coverage --check pycsl`. Fails on heading mismatch. **It cannot verify that the contract reflects the English — that is human review.**

Faithfulness review (periodic): an LLM-judge pass that, for each entry, reads the PyCSL contract, writes a candidate English description, and compares to the actual English with a similarity metric. Run weekly, not per-commit. Discrepancies open issues, not blocking CI. See §6 for why this is a soft gate.

### Step 4 — Stubs match contracts

Every entry in `calls-pycsl.md` has a stub in `Lib/`, and the stub's `#@` contract is byte-identical to the contract block in `calls-pycsl.md` (modulo whitespace).

CI check: `bin/stdlib-coverage --check stubs`. Fails on missing stub, missing symbol, or contract drift.

Reverse check in the same step: every stub symbol in `Lib/` has a matching entry in `calls-pycsl.md`. Dead stubs (defined but no longer used by `src/pycsl/`) are flagged as warnings, not errors — they may be intentional (covering an entry that's about to be re-introduced). Three releases of dead-stub status promotes to error.

### Step 5 — Self-annotation gate

A designated subset of `src/pycsl/` modules — initially small, growing over time — is annotated with `#@` contracts and verified by PyCSL itself. This is the final acceptance criterion: the stubs are *useful* iff the self-annotation succeeds.

CI check: `bin/run-self-annotation-suite.sh`. The suite proves the designated modules. Adding a module to the suite is a deliberate act, not automatic.

Initial suite (proposed): `src/pycsl/errors.py`, `src/pycsl/ir_schema.py`. Both are pure data-handling code, no libcst or Lark dependencies. Growing the suite is its own multi-quarter effort (see §8).

### Loop closure

After step 5: if it passes, the iteration is done. If it fails, the failure points either to a stub contract that is too weak (strengthen and loop), too strong (weaken and loop), or to PyCSL itself being unable to express the proof (a Module 4/6 gap — out of scope for this workplan, but the failure surfaces it).

The loop is the discipline. The tool enforces steps 1, 2, 4. Step 3 is the human gate. Step 5 is the success metric.

---

## 6. Why the English↔PyCSL check is soft

Mechanically verifying that a PyCSL contract is a faithful encoding of an English description is, in the general case, undecidable. The English itself is imprecise ("intelligently joins path components"); the PyCSL contract is precise but may underspecify. A CI gate that hard-fails on every such mismatch would either be useless (passing trivial mismatches) or block every PR (failing on cosmetic differences).

The pragmatic stance is two-layered:

- **Hard gate**: structural correspondence — every English heading has a PyCSL heading, every PyCSL heading has a stub.
- **Soft gate**: semantic correspondence — LLM-judge round-trip, periodic, opening issues rather than blocking commits.

This matches the *Worse-Is-Better* discipline from prior workplans: ship the mechanical checks now, let semantic verification be a follow-up signal that improves over time.

---

## 7. Initial bulk vs incremental discipline

### 7.1 Initial bulk (one-time)

The first pass:

1. Build `bin/stdlib-coverage` (the discovery tool).
2. Run `--discover` against the current `src/pycsl/` tree. Expect ~80–150 entries on first contact, mostly `os.path.*`, `re.*`, `json.*`, `ast.*`, `collections.*`, `typing.*`, builtins, and `str`/`list`/`dict`/`set` methods.
3. Populate `calls-english.md` from CPython docs. This is a long one-time effort; estimate one full-time week.
4. Translate to `calls-pycsl.md`. This requires design judgment per entry — what predicates to use, what postconditions to claim. Estimate two full-time weeks.
5. Stub `Lib/` to match. Mostly mechanical from `calls-pycsl.md`. Estimate one week.
6. Migrate `data/lib_stubs/` to `Lib/` (per §0.6) or reconcile naming. One PR.
7. Run step 5 (self-annotation) on the trivial initial suite. Iterate.

Total: roughly 4–6 weeks of dedicated effort, parallelizable on steps 3 and 4 across two engineers.

### 7.2 Incremental (per-PR, forever)

Any PR touching `src/pycsl/` runs `--check`. If new stdlib usage appears, the PR adds entries to all three artefacts in the same commit. The PR review checklist gains one line: *"If this PR uses a new stdlib API, are calls-english.md, calls-pycsl.md, and Lib/ updated?"*

This is the same per-PR discipline as the doc rule from §14 of the no_exception workplan: if a PR changes surface, the documentation moves with it.

### 7.3 CPython version migration (periodic)

When the pinned Python version bumps (e.g., 3.11 → 3.12), the workflow is:

1. Re-pin the CPython submodule.
2. Diff the relevant `.rst` files in `cpython/Doc/library/`.
3. For each affected entry, update `calls-english.md` if the English changed.
4. For each entry where the English changed, decide whether `calls-pycsl.md` and `Lib/` need updates.
5. Re-run the self-annotation suite.

Document this workflow once in `pycsl-stdlib-coverage.skill` (see §10).

---

## 8. Interaction with `no_exception`

The just-implemented `no_exception` feature compounds with stdlib coverage in two directions.

### 8.1 Stubs carry exception declarations

Every stub in `Lib/` declares the exceptions its modeled function can raise, via `raises { ... }` clauses. Examples:

- `dict.__getitem__` → `raises { KeyError }`
- `list.__getitem__` → `raises { IndexError }`
- `int(str)` → `raises { ValueError }`
- `os.path.exists` → `raises { }` (modeled as total)
- `open(path)` → `raises { OSError }`

The trigger conditions from `pycsl-exception-model.skill` Phase 1 cover language-builtin operations (`a/b`, `a[i]`). The stdlib analog covers library-function calls (`json.loads(s)`, `re.compile(p)`). Stub contracts encode them via standard `raises { ... }` rather than a new vocabulary.

### 8.2 Callers benefit from stub `no_exception`

When a stub is annotated `no_exception ValueError` with a precondition that discharges the trigger, callers automatically inherit the guarantee through inter-procedural propagation (Phase 1.4 of the no_exception plan). This is the payoff: as the stub library matures, `src/pycsl/` callers can claim `no_exception` for increasingly large code surfaces.

### 8.3 Implication for the workplan ordering

Stubs should be written `raises`-aware from day one. Adding `raises { }` clauses to existing stubs is a contract change; doing it retroactively is more painful than getting it right initially. The `calls-pycsl.md` entry template (§3.2) makes `raises` a required field.

---

## 9. Self-annotation: the north star

The acceptance criterion of the check loop is that `src/pycsl/` modules verify under their own contracts. The honest assessment of how far that goal is from where we are:

### 9.1 Modules tractable now

- `src/pycsl/errors.py` — pure exception class definitions, no logic. Tractable today.
- `src/pycsl/ir_schema.py` — validation logic over dict structures. Tractable with `dict.get` / `dict.__contains__` / `isinstance` stubs.
- Small utility modules if they exist (helpers, type predicates).

### 9.2 Modules tractable in 1–2 quarters

- `src/pycsl/Module5_IREmitter.py` — assuming AST visitor pattern can be expressed.
- Parts of `Module4_SemanticAnalyzer.py` — the simpler validators.

### 9.3 Modules hard or out of reach

- `src/pycsl/Module1_Ingestor.py` — libcst CST walking. Requires modeling libcst (a separate library coverage effort).
- `src/pycsl/Module2_Parser.py` — Lark LALR. Same.
- `src/pycsl/Module3_Weaver.py` — in-place AST mutation. Frame conditions on Python AST nodes is its own research problem.
- `src/pycsl/Module6_WhyMLTranspiler.py` — even refactored into `module6_whyml/`, the dispatcher patterns and string-building are hard. The dispatch tables are tractable; the recursive transpilation is the challenge.

### 9.4 Reading the milestone

"Stdlib coverage" is **complete** when the discovery tool reports zero gaps for `src/pycsl/`'s current API surface. "Self-annotation" is **complete** when every module in `src/pycsl/` is in the proven suite. The first is a *finite* engineering project (estimated 4–6 weeks). The second is a multi-year program of which this workplan is the foundation. Communicate the distinction clearly to stakeholders.

---

## 10. Documentation, skills, and corpus

### 10.1 `pycsl-software-architecture.skill` updates

- Section 1 (Repository layout) — add `Lib/`, `calls-english.md`, `calls-pycsl.md`, `bin/stdlib-coverage`. Remove `data/lib_stubs/` (or note the migration).
- Section 2 — note that Module 1 (Ingestor) consults `Lib/` for import resolution (not actual CPython sources).
- New short section on the stdlib coverage discipline, with a forward reference to the new skill below.

### 10.2 New skill: `pycsl-stdlib-coverage.skill` (CCB-tracked Configuration Item)

Contents:
- Purpose: governs the three-artefact discipline and the check loop.
- The five-step check loop with file paths.
- The trigger criterion (type-level vs call-level) with examples.
- The CPython version bump workflow.
- Cross-reference to `pycsl-exception-model.skill` for the `raises` integration.

This skill is to stdlib coverage what `pycsl-exception-model.skill` is to the no_exception feature: the canonical, change-controlled rulebook.

### 10.3 Reference manuals

- `docs/pycsl-concrete-syntax-reference.md` — no changes; no new annotations.
- `docs/pycsl-static-semantics-reference.md` — a short paragraph noting that stdlib calls resolve to `Lib/` stubs, and the trust-boundary implication (`Lib/` is part of the TCB).
- `docs/pycsl-translational-reference.md` — note the resolver step that maps `from os.path import join` to `Lib/os/path.py:join` rather than the actual CPython source.

### 10.4 `test-suite/annotations.md`

No new annotations — but a new section "Stub contracts" describing the convention for `#@` contracts in `Lib/` (no body, `raises` mandatory, no `no_exception` unless deliberate).

### 10.5 `README.md`

One line under "What PyCSL targets": *"PyCSL is being prepared for self-annotation; standard library coverage is tracked in calls-english.md / calls-pycsl.md / Lib/."*

### 10.6 Test corpus under `test-suite/corpus/python-reference/`

New subdirectory `stdlib/` mirroring `Lib/`:

```text
test-suite/corpus/python-reference/stdlib/
  os_path/
    join_basic_proves.py
    join_empty_components.py
    exists_proves.py
    ...
  re/
    compile_proves.py
    compile_invalid_pattern_raises.py
    pattern_match_proves.py
    ...
  json/
    dumps_proves.py
    loads_valueerror.py
    ...
  builtins/
    len_proves.py
    range_negative.py
    isinstance_proves.py
    ...
  str_methods/
    split_proves.py
    split_with_sep.py
    index_raises_valueerror.py
    ...
```

Conventions match the no_exception corpus: per-file docstring `"""expected: proves"""`, per-leaf `MANIFEST.toml`, three-level hierarchy. Each entry in `calls-pycsl.md` has at least one positive corpus file exercising its contract; entries with non-trivial preconditions get one positive and one negative.

Estimate: 200+ corpus files at steady state, ~50 at initial-bulk completion.

---

## 11. Anti-patterns

**Treating `Lib/` as documentation rather than as code.** It is read by PyCSL's resolver. A wrong contract there silently makes proofs unsound. The CCB process for `Lib/` changes is the same as for compiler code, not the same as for prose docs.

**Confusing "stdlib coverage" with "self-annotation".** The first is finite and bounded by `src/pycsl/`'s current API surface. The second is open-ended. Conflating them in roadmaps will produce wildly wrong estimates.

**Inlining stub bodies for "documentation".** A stub with a body looks helpful but invites two failure modes: (a) future readers think the body is normative, and (b) the body and the `#@` contract drift. Stubs end with `...` or `pass`. Always.

**Over-modeling stdlib semantics.** It is tempting to encode every nuance of `str.split` — the separator-not-found case, the maxsplit parameter, the whitespace-vs-explicit-separator differences. The right level is "what does `src/pycsl/` actually rely on?" Anything beyond that is YAGNI and increases TCB surface.

**Ignoring `raises` on stubs.** Skipping the `raises` clause "for now" is a debt that compounds: every caller using `no_exception` will eventually have to dig into the stdlib stub to figure out why their proof fails. Make `raises` mandatory in the stub template from day one.

**Vendoring CPython docs ad-hoc.** Pin a version, vendor as a submodule, document the version in `calls-english.md`. Ad-hoc copying of doc snippets without version pinning creates citations that rot silently.

**Hand-maintaining the report file.** `stdlib-coverage-report.toml` is regenerated by the tool, not hand-edited. If contributors are editing it, the tool is wrong or the workflow is wrong.

---

## 12. Out of scope

- **Coverage of external (non-stdlib) libraries** — libcst, Lark, click, etc. The same three-artefact discipline applies but is a separate, larger effort. The directory layout supports it (`Lib/_third_party/libcst/`) but the workplan does not commit to it.
- **Dynamic stdlib access** — `getattr(os, name)` and similar. The discovery tool flags these as warnings; resolving them is per-call-site work, not a systematic feature.
- **C-implemented stdlib internals** — when `dict.__getitem__` is actually a C-level slot in CPython, PyCSL still treats it as Python-level for modeling purposes. The C-extension boundary (UB-7.4 from the previous workplan) is the relevant defense if this assumption ever breaks.
- **Performance of `Lib/` resolution** — the resolver reads stubs lazily; performance tuning if needed is a separate concern.
- **Backwards compatibility with the existing `data/lib_stubs/`** — the workplan assumes a clean migration to `Lib/`. If existing downstream tooling reads from `data/lib_stubs/`, a transition strategy must be added.

---

## 13. Risk-ranked execution order

| # | Step | Risk | Estimate |
|---|---|---|---|
| 1 | Build `bin/stdlib-coverage` discovery tool | Low | 1 week |
| 2 | Run discovery on `src/pycsl/`, snapshot the report | Trivial | 1 day |
| 3 | Reconcile `data/lib_stubs/` → `Lib/` naming with architecture skill | Low (mechanical) | 2 days |
| 4 | Populate `calls-english.md` from CPython docs | Low (laborious) | 1 week |
| 5 | Translate to `calls-pycsl.md` with `raises` clauses | Medium (design per entry) | 2 weeks |
| 6 | Generate matching stubs in `Lib/` | Low (mechanical from step 5) | 1 week |
| 7 | Add `--check` CI gate to the build | Low | 2 days |
| 8 | Populate initial corpus under `stdlib/` | Low (laborious) | 1 week |
| 9 | Annotate and prove first self-annotation suite (errors.py, ir_schema.py) | Medium | 1–2 weeks |
| 10 | Document the discipline: `pycsl-stdlib-coverage.skill` and `docs/` updates | Low | 3 days |
| 11 | (Optional) Add LLM-judge soft gate for English↔PyCSL faithfulness | Medium | 1 week |

Each step is a PR. Steps 4 and 5 can parallelize across two engineers. Step 9 is where the workplan validates itself — if step 9 fails, steps 5–6 need revision.

Initial bulk: ~5–6 weeks calendar time with one engineer, ~3–4 weeks with two.

---

## 14. Summary

Three artefacts (`calls-english.md`, `calls-pycsl.md`, `Lib/`), one closed five-step check loop, one tool (`bin/stdlib-coverage`) to enforce the mechanical parts, one CCB-tracked skill (`pycsl-stdlib-coverage.skill`) to govern the discipline, and one north-star milestone (self-annotation of `src/pycsl/` itself).

The sketch as drafted is sound in shape but missing step 5, missing the terminology distinction between syscalls and stdlib APIs, missing the asymmetric-drift checks, missing the trigger-criterion refinement that the `Formatter` example actually implies, and unclear on `Lib/` vs `data/lib_stubs/`. Each of these is addressed above.

The interaction with `no_exception` is constant and beneficial: every stub declares `raises`, and well-annotated stubs compound into `no_exception` proofs for callers.

The honest framing of the goal: stdlib coverage is a finite, ~5–6 week project. Self-annotation of the full `src/pycsl/` is a multi-year program. The workplan ships the first; the second is its motivation, not its scope.

Same governing principles as before: cheap mechanical checks first, tooling enforces them, semantic checks are soft, documentation lands with code, the corpus is the gate, and trust in the artefacts must match their soundness role — `Lib/` is part of the TCB and is treated as such.
