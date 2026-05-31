# Phases 0–3 — Bootstrap

Phases for getting a fresh `<lang>csl` from "no code" to a stable
6-module pipeline. Load when scaffolding a new family member or
when revisiting an early-stage architectural decision.

---

## Phase 0 — Prior-art study

> **Squeeze →** none yet. Phase 0 is input-gathering, not
> constraint-setting. The squeeze begins at Phase 1.

Spend a few days reading. Do not start coding before this.

**Read at least:**

| System | Annotation language | What to absorb |
|---|---|---|
| Frama-C / WP plugin | ACSL | `requires`/`ensures`/`assigns`, ghost code, the `\result` / `\old` / `\at` operators, behavior clauses. |
| Creusot | Pearlite | Rust-specific contract shape, model types, prophecies, separation logic for borrows. |
| Dafny | Dafny | Tight integration between specs and implementation, automatic loop-invariant inference attempts. |
| F* | F* | Refinement types as the dual of contract annotations. |
| Why3 / WhyML | WhyML | The SMT backbone you are going to USE, not just learn from. Read `int.Int`, `int.EuclideanDivision`, `ref.Ref`, `array.Array`, `set.Fset`, `map.Map`. |
| Boogie | Boogie | Earlier-generation VC generator; useful for the calculus shape. |

**Deliverable**: `docs/prior-art.md` summarizing how each system
handles ~6 cross-cutting concerns:

1. Annotation surface (comment vs decorator vs separate file).
2. Verification dispatch (SMT first, fall back to interactive?).
3. Ghost code conventions (`#@ ghost x = …`).
4. Frame condition syntax (`assigns x[..]`, `modifies`).
5. Exception model (raises, panics, errors).
6. Termination / variant annotations.

**Architectural anchor decision**: Why3 is the default backend.
It provides the SMT dispatch layer, a mature WhyML language,
and a WP calculus you don't have to write. Anything else is a
much bigger project.

---

## Phase 1 — Minimum-viable prototype

> **Squeeze → S1 (contracts).** The first squeeze: a single
> function's contract must be provable by the SMT solver.
> End-to-end flow means the constraint is *mechanically checked*
> from day one.

A single Python file (`<lang>csl.py`) that does end-to-end flow
on one host-language pattern.

**Steps**:

1. **Strip `#@` lines** from the host source. Use the host's
   own parser (libcst for Python, tree-sitter for any
   language, swc for JS, syn for Rust, …). Preserve line numbers.
2. **Parse the contracts** with a minimal grammar — Lark for
   Python, nom for Rust, antlr otherwise. Start with:
   ```
   requires <expr>
   ensures <expr>
   assigns \nothing
   loop invariant <expr>
   loop variant <expr>
   ```
   Skip ghost code, `\old`, `\at`, quantifiers, exception clauses
   — all of those wait for Phase 4.
3. **Lower to WhyML**. The minimal Module 6 emits:
   ```whyml
   module Program
     use int.Int
     let f (x: int) : int
       requires { <requires> }
       ensures  { result = <ensures with \result→result> }
     = <translated body>
   end
   ```
4. **Dispatch to Why3**: `why3 prove -P Alt-Ergo,2.6.2, <file>.mlw`.
5. **Print the verdict** and exit code.

**Worked example**: a single function. GCD if you're feeling
classical:

```python
#@ requires a >= 0
#@ requires b > 0
#@ ensures \result >= 0
def gcd_simple(a: int, b: int) -> int:
    while b != 0:
        r = a % b
        a = b
        b = r
    return a
```

End-to-end verification of one file from the command line. That's
Phase 1.

**Anti-pattern to avoid**: trying to encode every host-language
construct here. The prototype's value is *end-to-end flow*, not
coverage. ~500 LOC is healthy; >2000 LOC means you're doing
Phase 3 inside Phase 1.

---

## Phase 2 — Host-language reference + traceability matrix

> **Squeeze → S3 (reference tests + traceability).** The
> traceability matrix squeezes the implementation: every grammar
> production must map to a reference test. Missing rows are
> visible gaps; verdict regressions fail CI.

Once Phase 1 verifies one function, scale by *driving from the
host language's grammar*.

**Inputs**:

- Host language reference manual or formal grammar. For Python:
  `ast` module docs + the Python grammar EBNF. For C: ISO C18
  draft. For Go: the Go specification. For Rust: the Rust
  reference.

**Build a traceability matrix** — a table mapping each grammar
production to a reference test:

```
| Production            | Test ID | Status | Module 6 handler        |
|-----------------------|---------|--------|-------------------------|
| ast.Assign            | 0001    | PASS   | _handle_assign_stmt     |
| ast.AugAssign         | 0002    | PASS   | _handle_aug_assign_stmt |
| ast.While             | 0003    | PASS   | _handle_while_stmt      |
| ast.For (over list)   | 0004    | PASS   | _handle_for_stmt        |
| ast.For (over range)  | 0005    | PASS   | _handle_for_range       |
| ast.Try / except      | 0010    | SKIP   | (Phase 4 — exceptions)  |
| ast.Match             | 0240    | FAIL   | (TODO: SMatch IR)       |
| ast.Lambda            | 0241    | SKIP   | (multi-week)            |
```

Cite [`test-suite/annotations.md`](../../../../test-suite/annotations.md)
as the shape this becomes once the *annotation* language is
formalized.

**Generate the corpus mechanically**: one small file per row
under `test-suite/corpus/<lang>-reference/`. A test runner
asserts the expected verdict. Verdict drift is a hard regression.

**Concrete deliverables**:

- `test-suite/corpus/<lang>-reference/0001-NNNN.<ext>` (numbered;
  never renumbered).
- `test-suite/traceability-<lang>.md` mapping grammar productions
  → test IDs → verdict → handler.
- `bin/run-reference-tests.sh` (or equivalent runner).

The corpus is now the discipline. Every prototype expansion
ships with the matching test.

---

## Phase 3 — First refactor: the 6-module compiler pattern

> **Squeeze → S6 (IR schema).** The Module 5→6 boundary becomes
> a machine-checkable contract. The IR schema squeezes both
> sides: Module 5 must produce valid IR, Module 6 must consume
> every valid IR node.

When the prototype hits ~1000-1500 LOC and feature growth slows,
refactor into the canonical 6-module pipeline (PyCSL's
discovered shape — see
[`config/skills/pycsl-software-architecture/SKILL.md`](../../pycsl-software-architecture/SKILL.md)
for the Python reference implementation):

```
Module 1 — Ingestor:           reads host source, extracts #@ blocks.
                               Preserves line numbers and comment scope.
Module 2 — Parser:             *CSL grammar → AST (the *CSL AST, not
                               the host AST).
Module 3 — Weaver:             attaches contracts to host AST nodes
                               (in-place csl_* fields).
Module 4 — Semantic Analyzer:  type checking, scope, contract
                               well-formedness.
Module 5 — IR Emitter:         annotated AST → JSON IR (the trust
                               seam — see Phase 6).
Module 6 — WhyML Transpiler:   JSON IR → Why3 .mlw text.
```

**Why this exact split**:

- Modules 1-3 are *host-language-specific*. The host parser
  (libcst/tree-sitter/syn) is here.
- Module 4 is *contract-specific*. Knows scope, types, frame
  conditions.
- Module 5 is the *trust seam*. The JSON IR is the boundary
  between "host language" and "verification". Phase 6's formal
  semantics later anchors here.
- Module 6 is *Why3-specific*. Can grow huge (the PyCSL
  Module 6 split into 10 sub-modules under `module6_whyml/`); keep
  it self-contained so swapping the backend (replacing Why3 with
  Boogie or Viper) is a Module-6-only change.

**Anti-pattern to avoid**: collapsing Modules 4 and 5 ("the
semantic analyzer can just emit IR directly"). Phase 6
formalization needs a stable IR; Phase 7's cross-check needs the
IR to be content-addressable. The Module 5 boundary is
load-bearing.
