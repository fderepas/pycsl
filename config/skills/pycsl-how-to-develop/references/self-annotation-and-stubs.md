# Self-Annotation Infrastructure + Library Stubs

Load when working on PyCSL's own self-annotation pipeline
(rocq2pycsl / lean2pycsl / pycsl_bridge) or adding library stubs
under `src/pycsl_lib/`.

## Self-Annotation Infrastructure

PyCSL is its own verification target. To annotate `src/pycsl/` with
contracts derived from the formal-semantics proofs under
`src/formal-semantics/{rocq,lean}/`, four companion packages live
alongside the core pipeline:

```text
src/
├── pycsl/              ← core pipeline (Module1–Module6 + agents)
├── pycsl_emit/         ← shared backend used by the three tools below
│   ├── ir/             ← language-agnostic IR (Var, BinOp, Forall, Divides, …)
│   │   └── json_io.py  ← --ir-dump JSON schema (pycsl-ir-dump v1)
│   ├── translator/     ← IR → PyCSL surface (operational/existential/guarded divides)
│   ├── emitter/        ← libcst-based annotation inserter
│   ├── checker/        ← subprocess wrapper for pycsl + verdict parser
│   └── config/         ← shared TOML schema (Config / FunctionSpec / PycslSettings)
├── rocq2pycsl/         ← Rocq .v   → PyCSL annotations (Lark default; SerAPI stub)
├── lean2pycsl/         ← Lean .lean → PyCSL annotations (Lark default; lean-script stub)
└── pycsl_bridge/       ← reconcile rocq + lean dumps; emit dual-attributed Python
    ├── canonicalizer/  ← IR → canonical IR (AC-flatten, alpha-rename, divides normal form)
    ├── reconciler/     ← canonical multiset diff + status (reconciled/rocq-only/lean-only/disagreement)
    └── linker/         ← pycsl-bridge.manifest.toml writer + drift checker
```

**Trust chain** (`pycsl-bridge-plan.md §5`):

```text
formal proof (Rocq or Lean)
       ↓ extract
shared pycsl_emit IR
       ↓ canonicalize + reconcile (pycsl_bridge)
PyCSL annotated Python  (with #@ proof rocq/lean per §2.1.12 where load-bearing)
       ↓ run pycsl
Why3 + SMT
       ↓
machine-checked verdict
```

The bridge closes the loop when *both* Rocq and Lean prove the same
contract: their canonical IRs must agree before annotated Python is
emitted. Disagreements surface as structured diffs in
`format_disagreement`, halting the pipeline by default.

### CLIs

| Tool | Entry | Use |
|------|-------|-----|
| `rocq2pycsl` | `rocq2pycsl --config CFG [--backend lark\|serapi] [--ir-dump PATH]` | Rocq → PyCSL pipeline; `--ir-dump` produces JSON consumed by the bridge |
| `lean2pycsl` | `lean2pycsl --config CFG [--backend lark\|lean-script] [--ir-dump PATH]` | Lean → PyCSL pipeline; same shape as above |
| `pycsl-bridge` | `pycsl-bridge --rocq-config R --lean-config L --python-src P [--manifest M] [--on-disagreement halt\|warn\|force]` | Reconciles both sides; emits annotated Python + manifest |

All three share `pycsl_emit` as their backend, so the IR is a single
shared contract — modifications to it must be coordinated across all
four packages (and reflected in `pycsl_emit/ir/json_io.py`'s schema
version).

### Tests

Each package has its own `tests/` tree:

- `src/pycsl_emit/tests/`         — IR round-trip, emitter goldens, checker
- `src/rocq2pycsl/tests/`         — extractor + translator + golden (double)
- `src/lean2pycsl/tests/`         — extractor + translator + golden (double)
- `src/pycsl_bridge/tests/`       — canonicalizer + reconciler + manifest + end-to-end golden

Run all four with:
```bash
PYTHONPATH=src python -m pytest src/pycsl_emit src/rocq2pycsl src/lean2pycsl src/pycsl_bridge
```

## Library Stubs

`src/pycsl_lib/` contains Python files with `#@ \trusted` contracts for standard library modules. These provide specifications for functions like `math.sqrt`, `random.randint`, etc., so the prover can reason about external calls without verifying their implementations.

Convention:
- One file per module (e.g., `math_stub.py`, `random_stub.py`)
- Each function has `#@ \trusted` and a full contract
- `#@ \trusted` in stub files is permanent (these are axioms about external code)
- `#@ \trusted` in user code marks genuinely unmodelable code (dict subscript assignment, external library types) — not for normal functions
