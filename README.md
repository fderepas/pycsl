# PyCSL 

PyCSL is an annotation language for Python. It enables to formally verify Python code using [Hoare Logic](https://en.wikipedia.org/wiki/Hoare_logic). An associated tool, `pycsl`, verifies the PyCSL annotations using [Why3](https://why3.lri.fr/). Why3 is a front end to SMT solvers such as Alt-Ergo and Z3. When those SMT solvers fail, Rocq can be used as the interactive theorem prover.

Documents define PyCSL [syntax](docs/pycsl-concrete-syntax-reference.md), [semantic](docs/pycsl-static-semantics-reference.md) and [translation to Why3](docs/pycsl-translational-reference.md).

For human-facing definitions of recurring verification terms such as
*witness*, *ghost code*, *ghost state*, *memory model*, and *solver budget*,
see [`docs/glossary/`](docs/glossary/).

---

## Example — Verifying Euclidean GCD

This walk-through introduces every concept that drives PyCSL by
incrementally annotating a single function. The finished file is shipped
as `test-suite/corpus/pycsl-reference/0342.py` and verifies end-to-end
under Why3 + Alt-Ergo with no `--no-proof`, no `\trusted`, and no human
proof scripting.

### Step 1 — The unannotated Python

```python
def gcd(a: int, b: int) -> int:
    x = a
    y = b
    while y != 0:
        r = x % y
        x = y
        y = r
    return x
```

Standard Euclidean algorithm: copy the parameters to mutable locals so
the contract can refer back to the originals, then reduce `(x, y) →
(y, x mod y)` until `y` reaches zero.

### Step 2 — State the specification

What we want to prove about `gcd(a, b)`:

- the inputs are non-negative (`a >= 0`, `b >= 0`),
- the result is non-negative, strictly positive when at least one
  input is, and divides both inputs, **and**
- the result is the *greatest* such common divisor — no larger
  positive integer also divides both inputs.

The last clause is what turns "result is a common divisor" into "result
is the *greatest* common divisor". Without it, a wrong implementation
returning `1` for positive inputs would satisfy the spec, because `1`
divides everything.

In PyCSL contract syntax — placed *before* the `def` line, each prefixed
by `#@`:

```python
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ ensures (a > 0 or b > 0) ==> \result > 0
#@ ensures (a > 0 or b > 0) ==> a % \result == 0
#@ ensures (a > 0 or b > 0) ==> b % \result == 0
#@ ensures \result == gcd(a, b)
#@ ensures (a > 0 or b > 0) ==>
#@   (\forall k; (k > 0 and a % k == 0 and b % k == 0) ==> k <= \result)
#@ assigns \nothing
```

Reading the tokens:

| Directive | Meaning |
|---|---|
| `requires P` | Caller's obligation: `P` must hold at function entry. Falsifying it is a *caller* bug. |
| `ensures P` | Function's guarantee: `P` holds at every return. `\result` denotes the return value. |
| `==>` | Logical implication. Use parentheses around the antecedent. |
| `a % b` | Python `mod` — `a % \result == 0` means "result divides a". |
| `\forall k; P ==> Q` | Universal quantifier (semicolon after binder). Here: for every `k`, if `k` is a positive common divisor then `k <= \result`. |
| `gcd(a, b)` | A call to the imported Why3 `gcd` function (introduced in Step 4) — *not* a recursive call to the Python function. Used here as a bridge so the SMT solver can substitute directly. |
| `True`, `False` | First-class boolean atoms in contracts (annotations.md §3.1.18). `#@ requires True` is the recommended form for "no precondition"; `#@ ensures False` is useful as a placeholder marking an intentionally-unprovable postcondition during incremental annotation. |
| `assigns \nothing` | Frame condition: no observable state is mutated (local variables don't count). |

Multiple `requires` / `ensures` lines are conjuncted.

### Step 3 — Annotate the loop

Hoare logic verifies a `while` by induction: pick an **invariant** that
holds before the loop, is preserved by every iteration, and combined
with the loop-exit condition implies the postcondition. Termination
needs a **variant** — a strictly-decreasing non-negative measure.

```python
def gcd(a: int, b: int) -> int:
    x = a
    y = b
    #@ loop invariant x >= 0
    #@ loop invariant y >= 0
    #@ loop invariant gcd(x, y) == gcd(a, b)
    #@ loop invariant (a > 0 or b > 0) ==> (x > 0 or y > 0)
    #@ loop variant y
    while y != 0:
        r = x % y
        x = y
        y = r
    return x
```

The load-bearing line is `gcd(x, y) == gcd(a, b)`: the Euclidean
identity that whatever `(x, y)` becomes, its gcd matches the original
pair. At loop exit (`y = 0`), this collapses to `gcd(x, 0) == gcd(a, b)`,
and the postconditions reduce to divisibility facts about `gcd(a, b)`.
The variant `y` strictly decreases because `x mod y < y` whenever `y > 0`.

### Step 4 — Hand the math to Rocq + Lean

The proof in Step 3 needs four mathematical facts SMT solvers cannot
discover on their own:

- `gcd a 0 = a` (loop-exit collapse),
- `gcd a b = gcd b (a mod b)` (Euclidean step, the invariant preservation),
- `a mod gcd(a, b) = 0` and `b mod gcd(a, b) = 0` (divisibility),
- `k > 0 ∧ k | a ∧ k | b → k ≤ gcd(a, b)` (**maximality** — the load-bearing
  fact for the "greatest" property; without it the spec would allow a
  buggy implementation that returns `1` for positive inputs).

These come from `test-suite/corpus/pycsl-reference/0342.proofs/`, where
the seven lemmas are **independently proved in both Rocq and Lean**.
PyCSL imports them as Why3 axioms via the `#@ proof` directive.
When the *same* `pycsl_target` is named for both provers, the
`proof2why3 cross-check` tool verifies that the two formalizations
state the same theorem (after canonicalization) — this is the **"Rocq +
Lean as Cross-Validated Spec Sources"** pattern.

```python
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_positive
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_a
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_b
#@ proof rocq Pycsl.Reference.Gcd.gcd_0
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof rocq Pycsl.Reference.Gcd.gcd_greatest
#@ proof lean Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof lean Pycsl.Reference.Gcd.gcd_result_positive
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_a
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_b
#@ proof lean Pycsl.Reference.Gcd.gcd_0
#@ proof lean Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_greatest
```

Why `gcd_greatest` *and* the divisibility axioms separately: the six
"common-divisor" axioms (`gcd_*_nonneg`, `gcd_*_positive`, `gcd_divides_*`,
`gcd_0`, `gcd_step`) pin down `gcd a b` by the Euclidean recurrence,
but none of them state — in a quantified form SMT can use — that
`gcd a b` is the *maximum* of all common divisors. `gcd_greatest`
fills that gap.

Why both Rocq *and* Lean: a typo in a Rocq theorem statement that
matches what the WhyML axiom needs is still a wrong axiom. With two
independent proof kernels stating the same fact, the chance of a
correlated mistake drops sharply. See
[`docs/cross-validated-spec-sources.md`](docs/cross-validated-spec-sources.md)
for the full architecture and
[`docs/pycsl-translational-reference.md`](docs/pycsl-translational-reference.md)
§T.2.10 for the WhyML emission rule.

### Step 5 — Run the verifier

```bash
PYTHONPATH=src .venv/bin/python -m pycsl.pycsl \
    test-suite/corpus/pycsl-reference/0342.py
```

Expected output (abridged):

```text
[*] Parsing and Semantic Analysis for '…/0342.py'...
[*] Running Proof Engine (provers: Alt-Ergo,2.6.2 → Z3,4.13.3)...
…
Sub-goal Postcondition of goal gcd'vc.
Prover result is: Valid (27.83s, 737520 steps).
[+] Verification SUCCESS! All contracts formally proven.
```

Every loop-invariant initialisation, every preservation step, the
variant decrease, the modulo guard, and all four postconditions are
discharged by Alt-Ergo using the seven imported axioms. No `\trusted`,
no `--no-proof`.

---

## Trust Chain

```
Layer 0 — Rocq / Lean type-checkers
   Machine-checked soundness theorem: pycsl_soundness
         ↓
Layer 1 — PyCSL #@ contracts on the Python implementation
   Structural faithfulness: frame conditions, loop termination,
   exhaustive dispatch over all 10 WP rule arms
         ↓
Layer 2 — Why3 + SMT solvers
   Output verification: the generated .mlw file is accepted by Why3

Layer 3 — Why3 val spec module  (self-annotate-layer3/pycsl-wp-spec.mlw)
   Semantic equivalence: one val per WP arm, ensures clause mirrors
   the Rocq fixpoint arm exactly.
   Machine-checked: Why3 clone/refinement proves generated code satisfies spec.
   Human-audited:   val spec written by inspection of Phase4_WP.v (line-by-line).
   See self-annotate-layer3/audit-guide.md for the full audit procedure.
```

Each layer covers what the others cannot:
- Layer 0 proves the WP calculus is mathematically sound.
- Layer 1 proves the Python code doesn't silently drop statements,
  corrupt state, or diverge from the formal structure.
- Layer 2 proves the actual generated WhyML satisfies the VCs.

---

## Cross-Prover Verification (`rocq2pycsl`, `lean2pycsl`, `pycsl-bridge`)

PyCSL ships three companion tools that mechanize the self-annotation
loop sketched above:

- **`rocq2pycsl`** — extract PyCSL contracts from a Rocq `.v` file
  (the formal-semantics proofs in `src/formal-semantics/rocq/`).
  Default backend is a hand-rolled Lark parser; a SerAPI subprocess
  backend is stubbed for later.

- **`lean2pycsl`** — extract PyCSL contracts from a Lean 4 `.lean`
  file (`src/formal-semantics/lean/`). Same architecture; default
  Lark backend; lean-script (lake env lean) backend stubbed.

- **`pycsl-bridge`** — read the JSON IR dumps from both converters,
  canonicalize each side, and confirm they agree before emitting
  annotated Python. Disagreements surface as structured diffs; the
  bridge halts by default rather than shipping mismatched contracts.

When a theorem must serve as a load-bearing Why3 axiom on the Python
side, the bridge emits an `#@ proof rocq <qualname>` /
`#@ proof lean <qualname>` line (`annotations.md §2.1.12`). The
former provenance-only `#@ proof rocq:` / `#@ proof lean:` directive
was removed from the language on 2026-05-27.

### Auditing `#@ proof` directives

`pycsl --audit-proof <file>` confirms each cited theorem actually
exists inside the matching `Module` / `namespace` nesting in the
proof files. The audit parses Rocq `.v` and Lean `.lean` files with
a namespace-aware state machine — the qualname `Pycsl.Reference.Gcd.gcd_step`
requires `Module Pycsl. Module Reference. Module Gcd.` (Rocq) or
`namespace Pycsl.Reference.Gcd` (Lean) to enclose the cited theorem.

Default proof dirs: `<file>.proofs/rocq/` and `<file>.proofs/lean/`
next to the Python file. Override with `--rocq-proofs-path DIR` and/or
`--lean-proofs-path DIR`. Use `--audit-proof-rocq` /
`--audit-proof-lean` to audit only one prover side.

```bash
pycsl --audit-proof test-suite/corpus/pycsl-reference/0342.py
# === Axiom-attribution audit (0342.py) ===
#   ✓ 0342.py:21  rocq: Pycsl.Reference.Gcd.gcd_result_nonneg
#   ...
#   Passed: 14 / Skipped: 0 / Failed: 0
```

Example invocation:

```bash
pycsl-bridge \
    --rocq-config proofs/rocq.toml \
    --lean-config proofs/lean.toml \
    --python-src   src/pycsl/parser.py \
    --output       src/pycsl/parser.annotated.py \
    --manifest     pycsl-bridge.manifest.toml
```

Result: an annotated Python source that PyCSL re-verifies via Why3
SMT, plus a `pycsl-bridge.manifest.toml` recording which Rocq and
Lean theorems contracted which Python function. See
`pycsl-bridge-plan.md §4` for the full workflow diagram.

### Rocq + Lean as Cross-Validated Spec Sources (`proof2why3`)

Beyond provenance documentation, PyCSL supports a stronger integration
mode: **Rocq + Lean as Cross-Validated Spec Sources**. In this mode,
proof-assistant theorems are imported as Why3 axioms via the
`#@ proof` directive (`annotations.md §2.1.12`), and a cross-check
pipeline ensures that the Rocq and Lean formalizations agree before any
axiom enters the verification.

- **`proof2why3`** — the cross-validation tool. Extracts theorem
  statements from Rocq (`.v`) and Lean (`.lean`) sources tagged with
  `pycsl_target` attributes, converts both to a canonical intermediate
  representation (alpha-normalized, AC-flattened, `nat`/`Nat` → `int`),
  and verifies semantic equality. On success, emits Why3 `axiom` blocks;
  on disagreement, halts with a structured diff.

This architecture provides **two-party verification** of the specification:
both Rocq and Lean kernels must independently confirm the theorem before
Alt-Ergo/Z3 can use it. The pattern is the foundation for PyCSL
self-hosting — annotating `pycsl`'s own source code with contracts derived
from the mechanized WP soundness proofs in `src/formal-semantics/`.

See [`docs/cross-validated-spec-sources.md`](docs/cross-validated-spec-sources.md)
for the full architecture plan and
[`test-suite/corpus/pycsl-reference/0342.py`](test-suite/corpus/pycsl-reference/0342.py)
for the worked example (Euclidean GCD with cross-validated spec axioms).

---

## Directory Layout

```
PyCSL/
├── src/
│   ├── pycsl/                          # Core pipeline (Python package)
│   │   ├── pycsl.py                    # CLI entry point
│   │   ├── Module1_Ingestor.py         # Reads .py, strips #@ annotation lines
│   │   ├── Module2_Parser.py           # EBNF grammar → contract AST
│   │   ├── Module3_Weaver.py           # Attaches contracts to Python AST nodes
│   │   ├── Module4_SemanticAnalyzer.py # Type/scope checking, variable resolution
│   │   ├── ConcurrencyChecker.py       # Static concurrency analysis (warnings)
│   │   ├── Module5_IREmitter.py        # Emits intermediate representation (JSON)
│   │   ├── Module6_WhyMLTranspiler.py  # Facade; JSON IR → .mlw (WhyML) for Why3
│   │   ├── module6_whyml/              # Module 6 split: stateless IR walks, identifiers,
│   │   │                               # SCC + auto-trust + abstract-ops + types +
│   │   │                               # expression / statement / preamble / function mixins
│   │   └── agents/                     # LLM agent scripts (see Agent Architecture)
│   ├── pycsl_emit/                     # Shared backend for the three tools below
│   │   ├── ir/                         #   IR + JSON round-trip (pycsl-ir-dump v1)
│   │   ├── translator/                 #   IR → PyCSL surface (with divides styles)
│   │   ├── emitter/                    #   libcst annotation inserter
│   │   ├── checker/                    #   subprocess wrapper for pycsl + verdict parser
│   │   └── config/                     #   shared TOML schema
│   ├── rocq2pycsl/                     # Rocq .v   → PyCSL annotations (Lark; SerAPI stub)
│   ├── lean2pycsl/                     # Lean .lean → PyCSL annotations (Lark; lean-script stub)
│   ├── pycsl_bridge/                   # Reconcile rocq + lean dumps; emit dual-attributed Python
│   │       ├── coordinator.py          # Orchestrator — owns the full retry loop
│   │       ├── agent-annotate.py       # Adds contracts to a Python file
│   │       ├── agent-splitter.py       # Call-graph analysis, topological sort
│   │       ├── agent-writer.py         # 3-agent writer coordinator
│   │       ├── agent-english-writer.py # English specification of a function
│   │       ├── agent-contract-writer.py# requires/ensures/assigns generation
│   │       ├── agent-invariant-writer.py # Loop invariants & variants
│   │       ├── agent-reconcile.py      # Diagnoses proof failures → JSON
│   │       ├── agent-script-update.py  # Applies reconciliation recommendations
│   │       ├── agent-script-update-mcp.py # MCP server enforcing write safety
│   │       ├── agent-rocq-proof-writer.py # Generates Rocq proofs for failed goals
│   │       ├── agent-infer-invariants.py  # Infers loop invariants from contracts
│   │       ├── agent-meta-evaluator.py # QA judge per attempt
│   │       ├── agent-meta-monitor.py   # Operational health watchdog
│   │       ├── agent-meta-reviewer.py  # Human-readable report generator
│   │       ├── llm_client.py           # LLM abstraction (Ollama, API)
│   │       └── schema_validator.py     # Validates agent I/O against schemas
│   ├── formal-semantics/               # Mechanized proofs of WP calculus soundness
│   │   ├── rocq/                       # Rocq (Coq) proofs: AST, SOS, WP, soundness
│   │   └── lean/                       # Lean 4 proofs (parallel development)
│   └── skill2rag/                      # Skill → RAG compiler (chunk, embed, index)
├── bin/                                # Launcher scripts and utilities
│   ├── run.sh                          # Full pipeline: annotate → prove → repair
│   ├── run-reference-tests.sh          # Run test suite (279+ reference tests)
│   ├── annotate.sh                     # Annotate a single file
│   ├── run-annotated.sh                # Run pycsl on tests/annotated/
│   ├── run-rocq-proofs.sh              # Replay Rocq proofs
│   ├── generate-rocq-proofs.sh         # Generate Rocq proof skeletons
│   ├── infer-invariants-from-contract.sh # Infer invariants from contracts
│   ├── update-rag.sh                   # Rebuild RAG index from skills
│   └── get-meta-info.sh               # Query meta-agent outputs
├── config/
│   ├── agents-config.json              # Model name, project-directory, tools
│   ├── agents/                         # Per-agent LLM prompt templates
│   ├── schemas/                        # JSON schemas for agent I/O validation
│   └── skills/                         # Skill files consumed by agents (RAG source)
│       ├── pycsl-annotate/             # Master annotation skill
│       ├── contract-writer/            # Contract-writing skill
│       ├── english-writer/             # English description skill
│       ├── invariant-writer/           # Loop/class invariant skill
│       ├── polish-skill/               # Post-processing rules
│       ├── rocq-prover/                # Rocq proof generation skill
│       └── pycsl-how-to-develop/       # Developer guide skill
├── data/
│   ├── embeddings/                     # Generated RAG index (skills_index.json)
│   └── lib_stubs/                      # Library stubs with trusted contracts
├── test-suite/
│   ├── annotations.md                  # Authoritative annotation reference
│   ├── traceability-pycsl.md           # Annotation ref → test ID mapping
│   ├── corpus/
│   │   ├── pycsl-reference/            # Reference tests (0001–0510+)
│   │   ├── negative/                   # Expected-failure tests
│   │   └── python-reference/           # Python semantics tests
│   ├── runner/                         # Static/dynamic oracle, evaluator
│   ├── instrumenter/                   # CSL-to-Python contract instrumenter
│   └── run_suite.py                    # Dual-oracle test runner
├── tests/
│   ├── to_annotate/                    # Input Python scripts (unannotated)
│   └── annotated/                      # Auto-generated annotated scripts
├── metrics/                            # Runtime logs and meta-agent outputs
│   ├── logs/                           # Captured stdout/stderr per attempt
│   ├── evaluator/                      # Per-attempt QA evaluation JSON
│   ├── monitor/                        # Per-file operational health JSON
│   └── reviewer/                       # Human-readable reports
├── docs/                               # Reference documents
│   ├── glossary/                       # Human-facing glossary (witness, ghost code, memory model, ...)
│   ├── pycsl-concrete-syntax-reference.md  # Normative EBNF grammar
│   ├── pycsl-static-semantics-reference.md # Well-formedness rules
│   └── pycsl-translational-reference.md    # Translation T: Python → WhyML
└── pyproject.toml                      # Python project metadata
```

---

## Pipeline

```
Python file (.py)
    │
    ▼
Module1_Ingestor    ← reads file, separates code from #@ annotations
    │
    ▼
Module2_Parser      ← parses #@ lines using EBNF grammar → contract AST
    │
    ▼
Module3_Weaver      ← attaches contract AST nodes to Python AST nodes
    │
    ▼
Module4_SemanticAnalyzer  ← type/scope checking, variable resolution
    │
    ▼
ConcurrencyChecker  ← (warnings only) static concurrency analysis
    │
    ▼
Module5_IREmitter   ← emits intermediate representation (JSON)
    │
    ▼
Module6_WhyMLTranspiler   ← generates .mlw (WhyML) file
    │
    ▼
Why3 / Alt-Ergo / Z3      ← SMT solver proves or rejects the goals
    │
    ▼ (on SMT failure, optional)
Rocq proof companion      ← manual interactive proofs via --rocq
```

---

## Usage

### Verify a single file

```bash
pycsl myfile.py
```

### CLI options

| Flag | Effect |
|------|--------|
| `--no-proof` | Skip prover — only check that valid WhyML is generated |
| `--keep-mlw` | Keep the `.mlw` file next to the input for inspection |
| `--fun NAME` | Only verify the named function (and call-deps). Repeatable |
| `--deep` | Recursively resolve transitive imports |
| `-p PROVER` | Use a specific prover (e.g. `Alt-Ergo,2.6.2,`) |
| `--provers LIST` | Comma-separated prover fallback chain |
| `--memory-model M` | `hoare` (default), `typed`, `store`, or `concurrent` |
| `--rocq DIR` | On SMT failure, generate Rocq proof skeletons in DIR |
| `--rocq-proofs [DIR]` | Replay pre-existing Rocq proofs from DIR |

### Selective function verification

```bash
# Only verify foobar and its transitive call-dependencies
pycsl --fun foobar myfile.py

# Verify multiple specific functions
pycsl --fun foobar --fun helper myfile.py
```

Functions not selected become trusted stubs: their contracts are assumed
as axioms, but their bodies are not checked.

### Multi-file verification

PyCSL automatically resolves `from ... import ...` and `import ...` statements
to local source files. Imported functions are injected as trusted stubs
(contracts assumed, bodies not re-verified).

```bash
pycsl dir2/file2.py         # auto-imports from local files
pycsl --deep file.py        # recursive transitive resolution (A→B→C)
```

External modules (stdlib, third-party) are skipped — add `\trusted` stubs
in `data/lib_stubs/` if callers need their contracts.

### Full annotation pipeline (annotate → prove → repair loop)

```bash
./bin/run.sh
```

### Run reference tests

```bash
./bin/run-reference-tests.sh                        # all tests
./bin/run-reference-tests.sh --start-at 200         # skip 0001–0199
./bin/run-reference-tests.sh --start-at 194 --stop-at 195  # range
```

Tests support `# pycsl-flags: ...` (extra CLI flags) and
`# pycsl-expected: FAIL` (expected-failure) directives in file headers.

### Rocq interactive proofs

When SMT solvers fail on a verification condition (VC), Rocq (Coq) proof
skeletons can be
generated and completed manually:

```bash
pycsl --rocq proofs/ myfile.py    # generates .v files in proofs/
# ... complete proofs in .v files ...
pycsl --rocq-proofs proofs/ myfile.py   # replays completed proofs
```

### Rocq + LLM helper

To keep the fast path clean, but automatically fall back to Rocq proof
generation plus the LLM Rocq proof writer on failure, use:

```bash
./bin/pycsl-prove-with-llm.sh myfile.py
```

Behavior:

1. Run normal `pycsl myfile.py`
2. If it succeeds, exit with no extra proof artifacts
3. If it fails, create `myfile.proofs/`, generate `.v` skeletons, run
   `agent-rocq-proof-writer.py`, then replay with `--rocq-proofs`

---

## Memory Models

PyCSL supports four memory models, selected via `--memory-model`:

| Model | Description | Use case |
|-------|-------------|----------|
| `hoare` | WhyML `ref` cells + `array` types (default) | Simple imperative code |
| `typed` | Flat memory map with `\valid`/`\separated` | Pointer-like reasoning |
| `store` | Same as typed, different heap name | Alternative flat memory |
| `concurrent` | Hoare + shared state + mutex invariants | Multi-threaded code |

For the human-facing terminology, see
[`docs/glossary/memory-model.md`](docs/glossary/memory-model.md). For the deeper
technical design discussion, see [`docs/memory_model.md`](docs/memory_model.md).

### Concurrent model

```python
#@ shared counter
#@ mutex_invariant lock_counter: counter >= 0
#@ \diverges
#@ thread_entry
def worker() -> int:
    #@ critical lock_counter
    counter += 1
    return 0
```

Critical sections use havoc+assume/assert to model mutex semantics:
shared variables are havoced, the mutex invariant is assumed on entry
and asserted on exit.

---

## PyCSL Contract Language (Quick Reference)

| Annotation | Scope | Purpose |
|---|---|---|
| `#@ requires <expr>` | Function / method | Precondition |
| `#@ ensures <expr>` | Function / method | Postcondition; `\result` is the return value |
| `#@ assigns <targets> \| \nothing` | Function / method | Frame condition |
| `#@ variant <expr>` | Function / method | Termination measure (recursive functions) |
| `#@ \diverges` | Function / method | Function may not terminate |
| `#@ \trusted` | Function / method | Body not verified; contracts assumed as axioms |
| `#@ raises E when cond` | Function / method | Exceptional postcondition |
| `#@ loop invariant <expr>` | `while` / `for` | Inductive property |
| `#@ loop variant <expr>` | `while` / `for` | Termination measure |
| `#@ class invariant <expr>` | `class` | Type-level invariant |
| `#@ ghost x = e` | Statement | Ghost variable (spec-only) |
| `#@ ghost x += e` | Statement | Ghost variable update |
| `#@ label L` | Statement | Program point for `\at(e, L)` |
| `#@ shared x` | Module | Shared variable (concurrent model) |
| `#@ mutex_invariant name: expr` | Module | Mutex invariant (concurrent model) |
| `#@ critical name` | Statement | Critical section (concurrent model) |

### Special atoms

| Atom | Meaning |
|------|---------|
| `\result` | Return value (in `ensures` only) |
| `\old(e)` | Value of `e` at function entry |
| `\at(e, L)` | Value of `e` at label `L` |
| `\length(arr)` | Array/list length |
| `\valid(arr, n)` | Array bounds validity |
| `\separated(a, na, b, nb)` | Non-overlapping memory regions |
| `\is_sorted(arr, lo, hi)` | Array sortedness |
| `\sum(arr, lo, hi)` | Array element sum |
| `\nothing` | Empty assigns frame |
| `\forall x; body` | Universal quantifier |
| `\exists x; body` | Existential quantifier |

### Operators in contracts

`==`, `!=`, `<`, `>`, `<=`, `>=`, `+`, `-`, `*`, `//`, `%`,
`and`, `or`, `not`, `==>` (implies), `<==>` (iff)

### Quantifiers

```python
#@ requires \forall i; 0 <= i and i < n ==> arr[i] >= 0
#@ ensures \exists j; 0 <= j and j < n and arr[j] == target
```

Bound variable separated from body by `;`, always typed as `int`.

---

## Class Support

### Classes as mutable records

Every Python class becomes a WhyML mutable record type.  Methods receive
`(self: classname)` as their first parameter.

```python
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    def increment(self, amount: int) -> int:
        self._value += amount
        return self._value
```

→ WhyML:

```whyml
type counter = { mutable _value: int }

let counter__increment (self: counter) (amount: int) : int
  requires { (amount >= 0) }
  ensures  { (self._value = ((old self._value) + amount)) }
=
  self._value <- self._value + amount;
  self._value
```

### Class invariants

A `#@ class invariant` annotation placed before the `class` keyword
declares a property checked at every method boundary:

```python
""  # pycsl
#@ class invariant self._value >= 0
class Counter:
    def __init__(self):
        self._value = 0
```

→ WhyML:

```whyml
type counter = { mutable _value: int }
  invariant { _value >= 0 }
  by { _value = 0 }
```

The `by { ... }` initializer witness is derived automatically from `__init__`
assignments.

---

## Agent Architecture

### Annotation pipeline (per file)

```
agent-annotate.py
├── (single-function path) — direct LLM call using pycsl-annotate skill
└── (multi-function path) — delegates to:
    └── agent-splitter.py — call-graph analysis, topological sort
        └── agent-writer.py — per-function annotation (3-agent pipeline)
            ├── agent-english-writer.py  — English spec of the function
            ├── agent-contract-writer.py — requires/ensures/assigns
            └── agent-invariant-writer.py — loop invariants & variants
```

### Coordinator loop (per file, up to 10 retries)

```
coordinator.py
├── agent-annotate.py       → produces annotated .py in tests/annotated/
├── pycsl (proof)           → exit 0 = pass, exit 1 = fail
│   (if fail)
├── agent-reconcile.py      → diagnosis + recommendation JSON
├── agent-script-update.py  → applies fix via MCP
├── agent-meta-evaluator.py → QA re-check
└── (retry)
```

### Inter-agent data flow

All agents communicate via **files on disk**, invoked as subprocesses by the
coordinator.

| Step | Writer | File(s) | Reader |
|------|--------|---------|--------|
| Annotate | `agent-annotate` | `tests/annotated/*.py` | `pycsl` |
| Prove | `pycsl` | `out.std`, `out.err` | `agent-reconcile` |
| Reconcile | `agent-reconcile` | `reconcile_<file>.json` | `agent-script-update` |
| Update | `agent-script-update` | modified agent or skill file | coordinator |
| Evaluate | `agent-meta-evaluator` | `metrics/evaluator/<stem>_<N>.json` | `agent-meta-reviewer` |
| Monitor | `agent-meta-monitor` | `metrics/monitor/<stem>.json` | `agent-meta-reviewer` |
| Review | `agent-meta-reviewer` | `metrics/reviewer/<stem>.json` + `.md` | human / CI |

All inter-agent JSON files are validated against schemas in `config/schemas/`.

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | All files passed |
| `1`  | Generic error |
| `72` | Max retries (10) exhausted for at least one file |
| `73` | Loop detected — identical recommendation 3× in a row |

---

## Library Stubs

`data/lib_stubs/` contains Python files with `#@ \trusted` contracts for
standard library and third-party modules (math, os, sys, json, collections,
threading, numpy, etc.).  These provide specifications so the prover can
reason about external calls without verifying their implementations.

Additionally, PyCSL's own pipeline modules (Module1–Module6) have self-referential
stubs for self-verification experiments.

---

## Skills and RAG

Agent LLM prompts are driven by **skills** in `config/skills/`.  Each skill
is a Markdown file (`SKILL.md`) with YAML frontmatter containing rules,
examples, and constraints.

Skills are compiled into a vector index by `src/skill2rag/`:

```bash
./bin/update-rag.sh    # must be run after any skill change
```

This produces `data/embeddings/skills_index.json`, queried by agents at runtime.

---

## Formal Semantics

Mechanized proofs in `src/formal-semantics/` establish the soundness of the
WP calculus for PyCSL's core language subset:

| Prover | Directory | Phases |
|--------|-----------|--------|
| Rocq (Coq) | `src/formal-semantics/rocq/` | AST → State → SOS → Desugar → WP → Soundness |
| Lean 4 | `src/formal-semantics/lean/` | Parallel development |

These proofs cover arithmetic, assignment, sequencing, if/else, and while
loops.  Constructs beyond the core (classes, exceptions, arrays) are modeled
using Why3's built-in theories.

---

## Test Suite

The reference test suite contains **279+ test files** in
`test-suite/corpus/pycsl-reference/` covering all annotation features.

- **`test-suite/annotations.md`** — Authoritative annotation reference (never
  renumber existing sections)
- **`test-suite/traceability-pycsl.md`** — Maps annotation refs to test IDs
- **`test-suite/run_suite.py`** — Dual-oracle runner (static + dynamic)
- **`test-suite/instrumenter/`** — Instruments contracts as Python assertions

Test files support directives:
```python
# pycsl-flags: --memory-model typed --no-proof
# pycsl-expected: FAIL
```

---

## Configuration

Edit `config/agents-config.json` to change the LLM model or project directory:

```json
{
  "model": "claude-sonnet-4.6",
  "project-directory": "./my_project",
  "skill-annotate": "skill-annotate.md"
}
```

The update agent may only modify agent scripts or skill files — writing to
`tests/annotated/` is blocked by the MCP server.
