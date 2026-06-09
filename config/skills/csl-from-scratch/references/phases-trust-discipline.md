# Phases 7–10 — Trust discipline

The verifier exists; it formalizes correctly; it verifies itself
and real programs; and CI guards the trust seam permanently.
Load when planning TCB-reduction work, when stubbing stdlib /
third-party libraries, when verifying real applications, or when
designing the continuous-trust gate.

---

## Phase 7 — TCB reduction loop

> **Squeeze → S7 (TCB inventory) + S9 (auto-trust tracking).**
> Every trust assumption is named and tiered. `Print Assumptions`
> squeezes the formal side; auto-trust counts squeeze the
> implementation side. The TCB can only shrink; growth requires
> justification.

The verifier's TCB starts large. Catalog the trust assumptions
explicitly per tier (see [cross-cutting-concerns.md](cross-cutting-concerns.md)
for the tier glossary), then close them iteratively. Each
closure is a separate PR / ticket.

**Per-tier targets**:

- **Tier 0a → 0a (no change, just smaller)**: every named axiom
  in the formal-semantics module is a target. Replace each with
  a proved Lemma. PyCSL's trajectory eliminated
  `module6_encodes_mlw`, `why3_validates_emitted`,
  `enrich_main_cert` — see items 21-25 in
  `closer-to-code-execution-status.md`.
- **Tier 1 (named external axioms)**: each is either replaceable
  (replace with a proved Lemma — see above) or genuinely
  external (`altErgoCorrect` is irreducibly Tier 1; mitigation
  is dual-solver dispatch).
- **Tier 2 (`\trusted reviewer:` modules)**: shrink by proving
  more of their bodies under full proof; OR refactor to push
  the trusted boundary downward.
- **Tier 3 (meta-level: parsers, canonicalizers)**: the
  `proof2why3` pipeline lives here. Mitigations:
  parity tests, negative tests, hand-eyeballing during registry
  updates.
- **Tier 4 (tool stack)**: not your problem. Pin versions; trust
  the upstream community.

**Cadence**: quarterly. PyCSL's example trajectory (see
[`closer-to-code-execution-status.md`](../../../../closer-to-code-execution-status.md)):

- **Q1**: framework + Module 1-3 trust assignment.
- **Q2**: Hoare-WP correctness (`wp_gen_correct`).
- **Q3**: Why3 trust-certificate cert-as-witness refactor.
- **Q4**: IR boundary closing — `ir_to_stmt` + round-trip
  theorem + byte-diff against Module 5's actual JSON output.

**End-state metrics that mark "TCB stable"**:

- Rocq side: zero PyCSL-specific axioms.
  `Print Assumptions <main_soundness_thm>` returns only
  `propositional_extensionality`,
  `functional_extensionality_dep`.
- Lean side: visible axioms ≤ 3; all named, all rationalized.
- Mechanical cross-check (Phase 10) runs on every `make`.

---

## Phase 8 — Self-annotation

> **Squeeze → S4 (self-annotation) + S8 (real-world tests).**
> The ultimate squeeze: the verifier must verify *itself*.
> This catches gaps no external test can: annotation-language
> holes, Module 6 emission gaps, parser blind spots. If the
> verifier can't express contracts about its own logic, the
> annotation language is incomplete.

The verifier annotates its own implementation. This is the
*dog-fooding* phase. It catches three classes of bug that no
external test catches:

1. **Annotation-language gaps** — the verifier can't express a
   contract it needs about its own logic.
2. **Module 6 emission gaps** — the WhyML transpiler can't handle
   a host pattern in its own source (e.g., set-union, dict
   truthiness, certain frame conditions).
3. **Modules 1-3 limits** — the host-language parser or weaver
   has blind spots its own code exercises.

**The pattern**:

- Mirror copy under `src/self-annotate/src/` carrying real
  bodies + `#@` annotations + selective `\trusted reviewer:`
  escape hatches for shapes that can't be expressed yet.
- Anti-drift gate: a signature-equality check that ensures the
  mirror's function/class signatures match the canonical
  source. PyCSL's pattern: `bin/self-annotate-mirror-check.sh`.
- Body-sync mechanism: when the canonical source changes, sync
  bodies into the mirror without clobbering the mirror's
  annotations. PyCSL's pattern: `bin/sync-mirror-bodies.py` (a
  libcst-based per-FunctionDef merger).

The PyCSL self-annotation working invariants:

- `make self-annotate-verify` + sample of full-proof reference
  tests + pytest + mirror-check + self-annotation suite after
  any change.
- Single canonical mirror only; old `attic/{rocq,lean}/`
  mirrors are dead.
- Blocker SHAPE is the durable identifier (line numbers drift).

**Self-annotation is where the architecture's promises become
real**. A *CSL that can't verify its own implementation is
under-built.

---

## Phase 9 — Standard library + memory models

> **Squeeze → S8 (real-world tests).** Stdlib stubs squeeze
> the annotation language against real API surfaces. Memory
> models squeeze the WP calculus against real mutation patterns.
> Both force the *CSL beyond toy examples.

Two parallel scaling axes that turn the *CSL from a research
prototype into something useful on real programs.

### 9.1 Standard library coverage

Real programs use stdlib. The *CSL must model the standard
library surface so that verified code can call stdlib functions
under contract.

**The methodology**: derive `\trusted reviewer:` stubs from the
**official API documentation** — `https://pkg.go.dev/std` for
Go, `https://docs.python.org/3/library/` for Python, MDN for
JavaScript, the Rust stdlib docs for Rust. The English
description in the official docs *is* the specification; the
stub translates that English into a machine-checkable *CSL
contract.

**Example — `strings.Contains` from Go stdlib**:

The official doc says:
> *Contains reports whether substr is within s.*

The stub becomes:

```go
//@ \trusted reviewer: go-stdlib
//@ ensures \result == true ==> exists i; 0 <= i && i + len(substr) <= len(s) && s[i:i+len(substr)] == substr
//@ ensures \result == false ==> forall i; 0 <= i && i + len(substr) <= len(s) ==> s[i:i+len(substr)] != substr
func Contains(s, substr string) bool
```

**Example — `len()` from Python stdlib**:

The official doc says:
> *Return the number of items in an object.*

The stub becomes:

```python
#@ \trusted reviewer: python-stdlib
#@ ensures \result >= 0
#@ ensures \result == len(obj)
def len(obj: Sized) -> int: ...
```

**Stub file structure**: one file per package under
`data/<lang>_lib_stubs/<package>.<ext>`:

```
data/go_lib_stubs/
  fmt.go          # fmt.Sprintf, fmt.Errorf, ...
  strings.go      # strings.Contains, strings.Split, ...
  strconv.go      # strconv.Atoi, strconv.Itoa, ...
  sort.go         # sort.Ints, sort.Slice, ...
  errors.go       # errors.New, errors.Is, ...
  math.go         # math.Abs, math.Max, ...
  os.go           # os.Open, os.ReadFile, ...
  io.go           # io.Reader, io.Writer interfaces
  sync.go         # sync.Mutex, sync.WaitGroup, ...
  net_http.go     # http.Get, http.ListenAndServe, ...
```

**Every stub function** carries:
- `\trusted reviewer: <lang>-stdlib` — marks it as Tier 2
  trust.
- `requires` / `ensures` clauses translating the English
  description into formal pre/postconditions.
- Conservative contracts: when the English is ambiguous, prefer
  weaker postconditions (more permissive) over stronger ones.
  Wrong contracts in trusted stubs are *soundness bugs*.

**Traceability**: maintain a coverage matrix mapping stdlib
packages → stub coverage percentage → reference tests:

```
| Package   | Functions | Stubbed | Tested | Coverage |
|-----------|-----------|---------|--------|----------|
| fmt       | 23        | 8       | 8      | 35%      |
| strings   | 46        | 15      | 15     | 33%      |
| strconv   | 18        | 6       | 6      | 33%      |
| math      | 72        | 12      | 12     | 17%      |
| os        | 45        | 0       | 0      | 0%       |
```

**Priority order**: stub the packages that real programs import
most. For Go: `fmt`, `strings`, `strconv`, `errors`, `sort`,
`math`, `os`, `io`, `sync`, `net/http`, `encoding/json`,
`context`. For Python: `os`, `sys`, `json`, `re`, `math`,
`collections`, `itertools`, `typing`, `pathlib`, `argparse`.

**Squeeze → S8**: each stub is a squeeze on the *CSL's
expressiveness. If the annotation language can't express a
stdlib function's contract, that's a language gap to fix in
Phase 4. If Module 6 can't emit the stub's WhyML, that's an
emission gap to fix in Phase 5.

**Imports** are mediated by Module 4's import classifier:
verified vs trusted vs unsupported, with explicit allow-lists.
Calling an unsupported stdlib function is a hard error, not a
silent skip.

### 9.1b Extreme-rigor pass

The §9.1 methodology above is the **baseline**: machine-checked
stubs derived from official docs, sufficient to keep real
programs compiling and to pin coverage. It is **not** the goal
state for stdlib modules whose semantics are mathematically
nontrivial — filesystem operations, math, crypto, format
serialization, anything with invariants worth proving.

For those modules, the goal state is **extreme rigor (ER)**:
body-verification where feasible, axiom-anchored otherwise, with
each remaining `\trusted` carrying a feature-plan citation that
names what blocks promotion. See
[`stdlib-extreme-rigor.md`](stdlib-extreme-rigor.md) for the
full discipline, the canonical case study
(`unix-filesystem/UnixInodeFileSystem.py`), the acceptance
checklist, and the escalation ladder.

Three load-bearing properties of an ER pass:

1. **Body-first.** A method that could be body-verified must not
   be `\trusted` for convenience. `\trusted reviewer:` is a
   tool, not a default.
2. **Coq lemmas for SMT timeouts.** When Z3 hangs on a
   mathematically-provable obligation, the move is
   `#@ proof rocq <qualname>` importing a kernel-checked theorem
   from the module's companion `.proofs/rocq/` directory — not
   `\trusted`.
3. **Each `\trusted` is actionable.** It carries a `cite:_note:`
   naming the precise IR-feature gap blocking promotion *and*
   the feature plan tracking that gap. Without that, the
   `\trusted` becomes permanent dark matter.

An ER pass is also a *forcing function for IR work*: it surfaces
the gaps that baseline stub work hides. The
UnixInodeFileSystem pass surfaced six IR-feature gaps, each
tracked in a feature plan. Treat the output of an ER
pass as having two deliverables: the annotated module *and* the
missing-feature plan it produced.

When ER is in scope, the feature plan driving the pass must
carry `**Acceptance:**` blocks per phase, enforced by
`bin/agent-feature-supervisor` (see
[`feature-supervisor-extreme-rigor.md`](../../../../feature-supervisor-extreme-rigor.md)
at repo root). Without supervisor-enforced acceptance, "done" is
self-declared — exactly the failure mode ER exists to prevent.

### 9.2 Memory models

Pick depending on the host language's mutation discipline:

| Memory model | When to use | What it gives |
|---|---|---|
| **`hoare`** (default) | Pure-functional contracts, no aliasing | Simplest VCs; works for arithmetic, recursion, immutable structures |
| **`typed` / `store`** | Mutable arrays, fields, references | Heap as `map loc int`; `ref t` for mutable references; supports `array.Array` from Why3 stdlib |
| **`concurrent`** | Multi-threaded code | Mutex discipline (lock orders), sharing invariants (`#@ shared x guarded_by mutex`), critical-section verification |

PyCSL pattern: `--memory-model {hoare,typed,store,concurrent}`
CLI flag; each model is a separate Module 6 emission pathway.
The default Hoare model covers ~80% of the reference corpus;
typed/store extends to mutable algorithms; concurrent extends
to thread-safety claims.

**Anti-pattern to avoid**: trying to make one emission pathway
cover all three models. The complexity multiplies and the
proofs become unintelligible.

### 9.3 Third-party library stubs

Real-world Go programs import `gorilla/mux`, `gin-gonic/gin`,
`go-redis/redis`, `gorm.io/gorm`. Real-world Python programs
import `requests`, `numpy`, `flask`, `sqlalchemy`, `pydantic`.
These are as pervasive as the stdlib — ignoring them means
the *CSL can only verify toy programs.

**Trust model**: identical to stdlib stubs — `\trusted
reviewer: <lib>-<version>` at Tier 2. The stub is the
verifier's model of the library's behavior; the library itself
is not verified.

**Selection criteria**: prioritize by import frequency in the
target ecosystem. For Go, the top-10 most imported non-stdlib
packages cover ~70% of real programs. For Python, PyPI
download stats give the ranking.

**Stub structure**: same as stdlib, under
`data/<lang>_lib_stubs/third_party/`:

```
data/go_lib_stubs/third_party/
  gorilla_mux.go       # mux.NewRouter, Route.HandleFunc, ...
  gin.go               # gin.Default, Context.JSON, ...
  go_redis.go          # redis.NewClient, Client.Get, ...
  testify_assert.go    # assert.Equal, assert.NoError, ...
```

```
data/lib_stubs/third_party/
  requests.py          # requests.get, Response.json, ...
  numpy.py             # np.array, np.zeros, ndarray ops, ...
  flask.py             # Flask, route, request, ...
  pydantic.py          # BaseModel, Field, validator, ...
```

**Contract derivation**: same methodology as stdlib —
translate the library's official documentation into
`requires` / `ensures`. For well-documented libraries
(requests, gin), the API docs are sufficient. For
under-documented libraries, derive contracts from the test
suite and README examples.

**Versioning discipline**: third-party APIs break across major
versions. Pin the stub to a specific major version:

```go
//@ \trusted reviewer: gin-v1
//@ requires ctx != nil
//@ ensures \result == nil ==> response was sent
func (c *Context) JSON(code int, obj interface{})
```

When a new major version changes the API, create a new stub
file (`gin_v2.go`) rather than modifying the existing one.

**Anti-pattern to avoid**: trying to stub every function in a
large library. Start with the 10-20 functions that appear in
real usage. Each stub is a trust commitment — keep the
surface small and correct rather than large and approximate.

### 9.4 Real-world application verification

The final scaling axis: verify actual production code, not
just reference tests. This is where all squeezes converge
(S1–S9) — if the *CSL can verify a real application, the
methodology works. If it can't, the gaps are visible and
trackable.

**Selecting a target application**:

- Start with a **small, self-contained utility** (100-500 LOC).
  A CLI tool, a config parser, a data validator. Not a web
  framework.
- The application must use only stdlib + already-stubbed
  libraries. Unsupported imports immediately reveal the stdlib
  coverage frontier.
- Pick an application whose correctness *matters* — a
  cryptographic primitive, a financial calculation, a safety
  check. Trivial applications don't test the *CSL's
  expressiveness.

**Annotation strategy for real-world code**:

1. **Auto-trust first**: run `<lang>csl` on the unannotated
   application. Every function gets auto-trusted. The initial
   auto-trust count is the "budget."
2. **Annotate bottom-up**: start with leaf functions (no
   callees). Write `requires` / `ensures` from the code's
   intent. Run `<lang>csl`. Each newly-proved function reduces
   the auto-trust count.
3. **Track the auto-trust burn-down**: the auto-trust count
   should decrease monotonically. Each PR that annotates
   functions reports the delta.

```
| PR  | Functions annotated | Auto-trust before | After | Delta |
|-----|---------------------|-------------------|-------|-------|
| #12 | parse_config        | 47                | 46    | -1    |
| #13 | validate_input      | 46                | 44    | -2    |
| #14 | compute_hash        | 44                | 43    | -1    |
```

4. **Identify blockers**: some functions will resist
   annotation because the *CSL can't express their contracts
   (e.g., higher-order functions, reflection, FFI). Each
   blocker is a tracked gap fed back to Phase 4 (annotation
   language) or Phase 5 (Module 6 emission).

**Deliverables**:

- `examples/<app>/` — the annotated application source.
- `examples/<app>/README.md` — auto-trust budget, blockers,
  annotation coverage percentage.
- Reference tests derived from the application's test suite
  (numbered 1000+).

**Squeeze → S8 (real-world tests)**: the application squeezes
the entire *CSL stack. Every layer is exercised:
- S1: contracts must be satisfiable on real logic, not just
  textbook arithmetic.
- S3: the reference corpus grows with real-world patterns.
- S6: the IR schema must handle real code shapes.
- S8: the stdlib/third-party stubs must model real API usage.
- S9: auto-trust on the application tracks the verifier's
  actual coverage ceiling.

**Graduation path**: start with one application. When the
auto-trust count reaches zero (full verification), pick a
larger one. The sequence — toy → utility → library →
service — mirrors the *CSL's expressiveness growth.

**Anti-pattern to avoid**: picking a flagship application too
early. If the stdlib stubs and annotation language are
immature, the auto-trust count stays high and no progress
is visible. Phase 9 presumes Phases 1-8 are substantially
complete.

---

## Phase 10 — Continuous trust reduction

> **Squeeze → all layers (S1–S9).** The final phase is the
> discipline of running every squeeze on every CI build.
> The cross-check, reverification, reference corpus, and
> `Print Assumptions` audit together form a gate that no
> trust regression can pass.

The work is never done. Establish a permanent discipline.

**Mechanical cross-check via `proof2why3`**: every `make
self-annotate-verify` (or equivalent CI gate) runs the 3-way
structural diff (Rocq AST ↔ Lean AST ↔ registry body) — the
build fails on registry-vs-prover drift. See
[`working-with-two-sources-of-truth.md`](../../../../working-with-two-sources-of-truth.md)
for the operational reference and
[`docs/cross-validated-spec-sources.md`](../../../../docs/cross-validated-spec-sources.md)
for the architecture sketch.

**Auto-emit + drift-aware merge.** Cross-check detects drift but
doesn't fix it. The next step is `proof2why3 emit`: an IR →
WhyML serializer that is the inverse of the cross-check parser
on the canonicalizable subset. Given a citation, it derives the
WhyML axiom body from the cross-checked canonical IR.

A naive overwrite regresses readability: canonical IR
alpha-renames bound variables to `v0/v1/…` instead of the
human-curated `a/b/k`. **Drift-aware merge** preserves the
hand-readable form where it's still semantically correct.
Partition qualnames into four buckets:

- **kept** — existing registry entry canonicalizes the same as
  the auto-generated form. Leave verbatim.
- **added** — new citation, no registry entry yet. Insert with
  the auto-generated body.
- **replaced** — canonical forms differ. Overwrite with the
  auto-generated body and report (this *is* the drift fix; the
  report signals attention).
- **orphan** — registry has an entry but no proof source.
  Defensive keep (audit-anchor stubs, third-party axioms).

PyCSL artifacts:
[`bin/proof2why3-emit.py`](../../../../bin/proof2why3-emit.py)
(per-file emit + `--check` round-trip),
[`bin/proof2why3-merge-registry.py`](../../../../bin/proof2why3-merge-registry.py)
(dry-run by default, `--write` to apply), Makefile targets
`check-axiom-registry-emittable`, `check-axiom-registry-drift`,
`sync-axiom-registry`. The first two are wired into
`make self-annotate-verify`.

The "registry as cache, refreshed drift-aware rather than blindly
overwritten" pattern generalizes — any auto-generated artifact
with a hand-curated readable variant benefits from kept/added/
replaced/orphan partitioning over wholesale regeneration.

**Reverify on every CI run**: `coqc` and `lake build` actually
recompile cited proofs; `Print Assumptions` / `#print axioms`
verify the assumption set stays in the kernel-axiom allow-list.
PyCSL implementation: `src/pycsl/audit_proof_reverify.py` +
`src/pycsl/proof_axiom_allowlist.py`.

**Reference corpus**: monotonic. New tests added; never
renumbered; PASS verdicts never silently downgrade. Verdict
drift fails CI.

**Public ledger**: every TCB-reduction step gets a numbered
entry in an execution-status doc. PyCSL's example:
[`closer-to-code-execution-status.md`](../../../../closer-to-code-execution-status.md)
items 1-61+. Future maintainers can see exactly which
assumptions came when and why.

**Multi-quarter cadence**: each quarter picks ONE TCB target
and closes it. Pace matters; the work is multi-year. See the
quarterly trajectory in Phase 7 above.
