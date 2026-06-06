# `rocq2pycsl` — Engineering Plan

A tool that treats a Rocq `.v` file as the *specification source* and emits
PyCSL `#@` annotations onto a hand-ported Python implementation, then asks
PyCSL/Why3/SMT to re-discharge the obligations independently.

The Rocq proof is **not transported** into Why3. It is used as a trusted
oracle for *what the contracts should say*. The SMT recheck replaces
refinement.

---

## 1. Goals and non-goals

**Goals**

- Given a Rocq function `f` and a Python function `f` with matching arity,
  produce a copy of the Python file with PyCSL annotations on `f` whose
  logical content matches the Rocq theorems about `f`.
- Discharge those annotations by invoking the PyCSL pipeline as a final
  round-trip check.
- Preserve the user's Python formatting, comments, and unrelated code
  untouched (libcst-based rewriting, not regeneration).
- Fail loudly and locally when a theorem uses Gallina features outside the
  supported subset, so the user can refactor or supply a manual override.

**Non-goals (v1)**

- Generating loop invariants for iterative Python implementations from
  inductive Rocq proofs.
- Translating Rocq proof terms into Why3 proof tasks.
- Supporting dependent types, higher-order quantification, or universe
  polymorphism in spec statements.
- Generating the Python body. The user hand-ports.

---

## 2. Architecture

```
rocq2pycsl/
├── extractor/          # Phase 1: get IR out of Rocq
│   ├── serapi.py       # subprocess wrapper around sertop
│   ├── sexp.py         # s-expression parser
│   └── selector.py     # picks the theorems that constitute the spec
├── ir/                 # IR: a small first-order proposition AST
│   ├── nodes.py        # Forall, Exists, BinOp, App, Var, Lit, Divides, ...
│   └── pretty.py
├── translator/         # Phase 2: IR -> PyCSL expression strings
│   ├── gallina.py      # the main rewriter
│   ├── opmap.py        # Gallina operator -> PyCSL operator
│   ├── divides.py      # special-case translation of (d | n)
│   └── names.py        # identifier mapping (Rocq -> Python)
├── emitter/            # Phase 3: rewrite the Python source
│   ├── locator.py      # find target def via libcst
│   ├── annotator.py    # insert leading-line #@ annotations
│   └── checker.py      # invoke `pycsl` and parse results
├── config/
│   ├── schema.py       # TOML schema
│   └── load.py
├── cli.py              # `rocq2pycsl` entry point
└── tests/
    ├── golden/         # (Rocq, Python, expected output, pycsl outcome) tuples
    └── unit/
```

**Data flow**

```
.v file ──┐
          ├──> SerAPI ──> sexp ──> IR ──> PyCSL expr strings ──┐
mapping ──┘                                                    │
                                                               ▼
                                  .py file ──> libcst tree ──> annotated .py
                                                                       │
                                                                       ▼
                                                                    pycsl
                                                                       │
                                                                       ▼
                                                              verification report
```

---

## 3. Phase plan with milestones

### Phase 0 — Scaffold (1–2 days)

- Project layout, `pyproject.toml`, lint/test config.
- Dependencies: `coq-serapi` (system), `libcst`, `typer`, `tomli`, `pytest`.
- Smoke-test: spawn `sertop`, feed it `(Add () "Definition x := 1.")`,
  parse the response.

### Phase 1 — Rocq extraction (1 week)

Goal: given a `.v` file, return a list of `(name, statement_ir)` pairs for
every `Theorem`/`Lemma`/`Function`/`Definition`/`Fixpoint`.

Substeps:

1. Wrap `sertop` in a request/response loop (`serapi.py`).
2. For each top-level vernac, request `(Query () (Definition <name>))` or
   `(Query () (Type <name>))` and parse the returned s-expression.
3. Build a tiny s-expression parser (`sexp.py`) — strings, lists, atoms.
4. Define the IR (see §4).
5. Translate sexp -> IR for the first-order subset.
6. Anything outside the subset becomes an `IR.Unsupported(reason, raw_sexp)`
   node so the translator can produce a useful error message instead of
   silently dropping content.

Deliverable: `extractor.load("Euclid.v")` returns the IR for `gcd`,
`gcd_divides`, `gcd_greatest`.

### Phase 2 — IR → PyCSL translation (1 week)

Goal: given an IR node, produce a PyCSL contract expression as a string.

Substeps:

1. Walker over IR producing PyCSL expression strings with explicit
   parenthesization (no precedence hacks).
2. Operator mapping table (see §5).
3. Identifier renaming using the mapping file.
4. Strip outer `forall` binders that match the target function's
   parameter list — these are absorbed into the function's parameters in
   PyCSL.
5. Detect `\result` placement: in a postcondition `forall a b, P (f a b)`,
   the application `f a b` becomes `\result`.

Deliverable: `translator.render(theorem_ir, mapping)` returns
`"a % \\result == 0"` (etc.) for `gcd_divides`.

### Phase 3 — Python rewriter (4–5 days)

Goal: insert leading-line `#@` annotations on the target `def`.

Substeps:

1. Parse the user's Python file with `libcst`.
2. Locate `def <python_name>` by AST search (not regex).
3. Build the annotation block:
   - one `#@ requires <expr>` per precondition
   - one `#@ ensures <expr>` per postcondition
   - `#@ \variant <expr>` if the Rocq definition used `{measure ...}`
   - `#@ assigns \nothing` if the Rocq function is pure (the default for
     `Function`/`Fixpoint`/`Definition` with no state)
4. Insert the block as leading-line comments before the `def` using
   libcst's leading-lines API. Preserve existing leading comments.
5. Write the result to the output path. Never mutate the input file.

Deliverable: round-trip on `euclid.py` produces the file we wrote
manually earlier.

### Phase 4 — Verification round-trip (2 days)

Goal: invoke `pycsl` on the annotated output and report.

Substeps:

1. Shell out to `pycsl <output.py>` with the user's prover settings.
2. Parse the goal-by-goal results (see PyCSL doc §9 — split-VC output).
3. Print a summary:
   `gcd: 6/6 obligations Valid` or
   `gcd: 4/6 Valid; gcd_greatest (ensures #2): Unknown (Alt-Ergo timeout)`.
4. Exit non-zero if any obligation is not Valid (configurable).

Deliverable: `rocq2pycsl --check euclid.v euclid.py` succeeds end-to-end.

### Phase 5 — Configuration and UX (3 days)

- TOML config file (see §6).
- Useful CLI flags: `--dry-run` (print to stdout), `--diff` (show patch),
  `--strict` (fail on any `IR.Unsupported`), `--no-check` (skip pycsl
  invocation).
- Helpful error messages with file:line cross-references back into the
  `.v` file.

### Phase 6 — Test corpus (ongoing, start in parallel with Phase 2)

- Golden tests: (`.v`, `.py`, expected annotated `.py`, expected pycsl
  outcome). Start with GCD, factorial, Fibonacci, list length, list sum,
  power, integer square root.
- Negative tests: theorems using unsupported features (higher-order
  quantifiers, dependent matches) must produce clear errors, not crashes.

---

## 4. The IR

Small enough to fit in one file:

```python
@dataclass class Var:       name: str
@dataclass class Lit:       value: int | bool
@dataclass class App:       fn: str; args: list[Node]
@dataclass class BinOp:     op: str; lhs: Node; rhs: Node
@dataclass class UnaryOp:   op: str; arg: Node
@dataclass class Forall:    var: str; ty: str; body: Node
@dataclass class Exists:    var: str; ty: str; body: Node
@dataclass class Divides:   d: Node; n: Node           # (d | n) in Coq Nat
@dataclass class Result:    pass                       # placeholder for \result
@dataclass class Unsupported: reason: str; raw: str
```

That covers the entire first-order PyCSL spec language plus `Divides`,
which is the one Gallina-specific predicate that needs a special-case
translation (see §5).

Theorems carry a header:

```python
@dataclass class Theorem:
    name: str
    binders: list[tuple[str, str]]   # (var, type)
    statement: Node
```

Functions:

```python
@dataclass class FunctionDef:
    name: str
    params: list[tuple[str, str]]
    return_ty: str
    measure: Node | None             # for Function with {measure ...}
    body: Node | None                # not used in v1; kept for future use
```

---

## 5. Translation rules

### 5.1 Logical and arithmetic operators

| Gallina | PyCSL | Notes |
|---|---|---|
| `forall x : T, P` | `\forall x; P` | T discarded (PyCSL types quantified vars as `int`); strip outer foralls bound by function params |
| `exists x : T, P` | `\exists x; P` | same |
| `P -> Q` | `P ==> Q` | when `P : Prop`; if `P : Type` (a function arrow), error |
| `P /\ Q` | `P and Q` | |
| `P \/ Q` | `P or Q` | |
| `~ P` | `not P` | |
| `P <-> Q` | `P <==> Q` | |
| `True`, `False` | `True`, `False` | |
| `n = m` | `n == m` | only when both sides are concrete data, not propositions |
| `n <> m` | `n != m` | |
| `n <= m`, `n < m`, `n >= m`, `n > m` | same | |
| `n + m`, `n - m`, `n * m` | same | |
| `Nat.div n m`, `n / m` | `n // m` | |
| `Nat.modulo n m`, `n mod m` | `n % m` | |
| `f x y` (pure) | `f(x, y)` | requires `f` to also exist as a pure Python with `#@ assigns \nothing` |

### 5.2 Divisibility

In Coq's `Nat` module, `(d | n)` is `exists k, n = d * k`. Two PyCSL
spellings are possible:

- **Faithful:** `\exists k; n == d * k` — closest to the definition, but
  Why3+SMT often struggles with existentials over unbounded integers.
- **Operational:** `n % d == 0` — what we actually want SMT to chew on,
  but requires a side condition. When `d = 0`, `n % d` is undefined in
  WhyML; when `d > 0`, `n % d == 0` is equivalent to divides.

Recommended: emit the operational form **guarded by a positivity check
inferred from context**:

- If the Rocq theorem also proves `d > 0` (or `d <> 0`), emit `n % d == 0`.
- If not, emit `(d == 0 and n == 0) or (d > 0 and n % d == 0)`.
- If the user prefers the existential, surface a `--divides-style=exists`
  flag.

This is the single most fiddly translation rule and the most likely place
to need user override.

### 5.3 Quantifier scoping

A theorem like

```coq
Theorem gcd_divides : forall a b, (gcd a b | a) /\ (gcd a b | b).
```

has two outer binders `a b` that exactly match `gcd`'s parameter list.
When translating to a postcondition on `gcd(a, b) -> int`, these are
**absorbed**: PyCSL contracts on `def gcd(a, b)` already scope `a` and
`b`. We emit:

```python
#@ ensures a % \result == 0
#@ ensures b % \result == 0
```

Splitting `/\` at the top level of a postcondition into separate
`#@ ensures` lines is cosmetic but more readable and gives finer-grained
goal reports from Why3.

### 5.4 `\result`

Within an absorbed-forall postcondition, the application of the target
function to the absorbed parameters becomes `\result`. Concretely, after
binder absorption, every occurrence of `gcd(a, b)` (or whatever the
Gallina spelling rewrote to) in the conclusion is replaced by `\result`.

If the Rocq theorem refers to the function applied to *non-parameter*
arguments — e.g. `gcd a 0 = a` — that is **not a postcondition**, it is
a lemma about the function's behavior on a specific input. Such theorems
are skipped for `ensures` generation but kept for documentation
(emit as a docstring comment, optional).

### 5.5 Variant

From `Function f a b {measure (fun n => <expr>) b}`, extract `<expr>`
with `n` substituted by `b`, and emit `#@ \variant <expr>`. For the
common idiom `{measure (fun n => n) b}` this collapses to
`#@ \variant b`.

For `{wf <rel> <expr>}` (well-founded ordering), emit
`#@ \variant (<expr>, <rel>)` per the PyCSL structural-variant syntax.

### 5.6 Purity

For v1, any function defined via `Definition`/`Fixpoint`/`Function`
without a monadic return type is treated as pure: emit
`#@ assigns \nothing`. Monadic returns (state, IO, error) are
unsupported and produce an explicit error.

---

## 6. Configuration

`rocq2pycsl.toml` in the project root:

```toml
[input]
rocq    = "proofs/Euclid.v"
python  = "src/euclid.py"
output  = "src/euclid.annotated.py"

[functions.gcd]
python_name      = "gcd"
spec_theorems    = ["gcd_divides", "gcd_greatest"]
precondition_theorems = []                  # rarely needed
arg_map          = { a = "a", b = "b" }     # default identity
divides_style    = "operational"            # or "exists"

[functions.gcd_iter]
python_name      = "gcd_iter"
spec_theorems    = ["gcd_divides", "gcd_greatest"]   # reuse the same spec
# loop invariants are NOT generated in v1; user adds them by hand

[pycsl]
extra_flags = ["--memory-model", "hoare"]
prover      = "Alt-Ergo,2.6.2,"
```

Selection precedence:

1. Explicit `spec_theorems` list in the config (highest priority).
2. In-source markers: `(* @pycsl-spec gcd *)` above a theorem.
3. Heuristic: any theorem whose statement mentions the function symbol.

Heuristic mode prints a list of what it selected so the user can see
what's happening. v1 should **default to requiring explicit selection**
because heuristic-only picks too many helper lemmas.

---

## 7. Worked example: GCD

Input `Euclid.v`:

```coq
Function gcd (a b : nat) {measure (fun n => n) b} : nat := ...

Theorem gcd_divides :
  forall a b, (gcd a b | a) /\ (gcd a b | b).

Theorem gcd_greatest :
  forall a b d, (d | a) -> (d | b) -> (d | gcd a b).
```

Input `euclid.py`:

```python
def gcd(a: int, b: int) -> int:
    if b == 0:
        return a
    return gcd(b, a % b)
```

Config:

```toml
[functions.gcd]
spec_theorems = ["gcd_divides", "gcd_greatest"]
```

Expected output:

```python
#@ ensures a % \result == 0
#@ ensures b % \result == 0
#@ ensures \forall d; (a % d == 0 and b % d == 0) ==> \result % d == 0
#@ assigns \nothing
#@ \variant b
def gcd(a: int, b: int) -> int:
    if b == 0:
        return a
    return gcd(b, a % b)
```

Notes on what happened:

- `gcd_divides`'s outer `forall a b` matched `gcd`'s params and got
  absorbed. The conjunction was split into two `ensures` lines.
- `gcd_greatest`'s outer `forall a b` got absorbed; the inner `forall d`
  did not (it's a fresh ghost variable) and remained as `\forall d; ...`.
- Divisibility `(d | a)` translated to `a % d == 0` per the
  operational-form rule, conditionally on `d > 0`. (The full guarded
  form `(d == 0 and a == 0) or (d > 0 and a % d == 0)` is omitted here
  for readability; v1 emits it unless the user opts into a stronger
  precondition.)
- `Function ... {measure (fun n => n) b}` produced `#@ \variant b`.
- The Rocq function being pure produced `#@ assigns \nothing`.

The round-trip then invokes `pycsl euclid.annotated.py` and confirms
each obligation discharges.

---

## 8. Known limitations and explicit scope cuts (v1)

- **Inductive types in specs.** A theorem like `forall l, length (rev l) = length l`
  uses `list` and `rev`. Unsupported. Workaround: user declares Python
  list operations as pure functions in PyCSL and provides a hand-written
  contract.
- **Higher-order quantification.** `forall f, P f` is rejected.
- **Dependent pattern matching.** `match x in vec n with ...` rejected.
- **Custom notations.** Anything beyond the standard `Nat`/`Z` notations
  is rejected unless the user supplies a translation rule in config.
- **Loop invariants.** Not generated. The user adds these by hand on
  iterative Python implementations.
- **Class invariants.** Not handled in v1. Rocq doesn't have a direct
  equivalent; user can supply class invariants manually.
- **Concurrency.** Out of scope for v1. Rocq proofs are sequential; PyCSL's
  concurrent memory model uses monitor invariants that don't have a
  natural Rocq counterpart.

---

## 9. Testing strategy

**Golden corpus**, each entry is a directory with:

- `spec.v` — the Rocq proof
- `impl.py` — the hand-ported Python
- `expected.py` — what the tool should emit
- `config.toml` — the configuration
- `outcome.txt` — expected `pycsl` verdict (counts of Valid/Unknown)

Initial corpus:

1. `gcd` (Euclid) — recursive
2. `factorial`
3. `fibonacci`
4. `list_length` (uses pure list helpers)
5. `power` (integer exponentiation)
6. `isqrt` (integer square root, with `\result * \result <= n` ensures)
7. `sum_to_n` (uses a pure recursive `sum` in the spec)
8. `min_of_two`

**Round-trip tests.** For every corpus entry, after the tool emits
`actual.py`, run `pycsl actual.py` and assert the verdict matches
`outcome.txt`. A regression here means either the translator drifted or
the PyCSL pipeline changed; both are useful signals.

**Negative tests.** A small set of `.v` files using unsupported features
(higher-order quantifier, dependent match, custom notation). Each must
produce a clear error pointing at the offending Rocq position.

**Property tests.** For arithmetic translation specifically, generate
random Gallina expressions in the supported subset, translate, and
re-parse the resulting PyCSL with PyCSL's own parser to confirm
round-trippability.

---

## 10. Open design questions

1. **Should the tool also generate a Python skeleton when no `impl.py`
   exists?** Probably yes in v2, as a `--scaffold` mode. v1 requires the
   user to hand-port.
2. **How to handle Rocq `Z` (integers) vs `nat` (naturals)?** PyCSL's
   `int` is unbounded signed. `Z` maps cleanly. `nat` requires an
   implicit `>= 0` precondition on every quantified variable — emit it
   automatically.
3. **What's the SerAPI dependency story?** SerAPI tracks Rocq versions
   tightly. The tool must pin a known-good Rocq+SerAPI pair and document
   it. `coq-lsp` is a possible alternative for v2.
4. **How to surface partial successes?** If 4/6 obligations verify, do we
   write the file anyway? Yes, but the report flags which ensures didn't
   discharge so the user can investigate or weaken.
5. **Should we round-trip the Python through PyCSL's parser before
   writing?** Probably yes — catches malformed annotations early, before
   the user runs `pycsl` themselves.

---

## 11. Estimated effort

A reasonable solo timeline, assuming familiarity with SerAPI and libcst:

- Phase 0: 2 days
- Phase 1 (extraction): 1 week
- Phase 2 (translation): 1 week
- Phase 3 (rewriter): 4–5 days
- Phase 4 (verification round-trip): 2 days
- Phase 5 (UX): 3 days
- Phase 6 (test corpus): runs in parallel from Phase 2; +3 days dedicated

Total: ~4 weeks to a working v1 that handles the corpus in §9.

---

## 12. References to consult during implementation

- **SerAPI**: Gallego Arias, *SerAPI: Machine-Friendly, Data-Centric
  Serialization for Coq*, Tech. Report, MINES ParisTech (2016).
  Repo: <https://github.com/ejgallego/coq-serapi>.
- **PyCSL annotation language**: the document we worked from earlier.
- **libcst**: Instagram's concrete-syntax tree library for Python source
  rewriting. <https://libcst.readthedocs.io>.
- **Why3**: Bobot, Filliâtre, Marché, Paskevich, *Let's verify this with
  Why3*, STTT 17(6), 2014.
- **Creusot** (architectural reference): Denis, Jourdan, Marché, ICFEM
  2022. <https://hal.science/hal-03737878>.
- **Coq extraction** (for the conceptual contrast): Letouzey's PhD;
  Sozeau et al., *Verified Extraction from Coq to OCaml*, PLDI 2024.
