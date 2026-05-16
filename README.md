# PyCSL — Self-Healing Formal Verification Pipeline

PyCSL is an agentic pipeline that takes Python scripts, annotates them with
Hoare-logic contracts using an LLM, verifies the annotations with the
[Why3](https://why3.lri.fr/) / Alt-Ergo proof engine, and automatically
repairs failures through a reconcile → update agent loop.

---

## Directory layout

```
PyCSL/
├── pycsl                   # Proof runner (calls Why3/Alt-Ergo)
├── run.sh                  # Main entry point (see Usage below)
├── tests/
│   ├── to_annotate/        # Input Python scripts (unannotated)
│   └── annotated/          # Auto-generated annotated scripts
├── metrics/                # Meta-agent outputs (created at runtime)
│   ├── logs/               # Captured stdout/stderr per attempt
│   ├── evaluator/          # Per-attempt QA evaluation JSON
│   ├── monitor/            # Per-file operational health JSON
│   └── reviewer/           # Human-readable report (JSON + Markdown)
└── agents/
    ├── coordinator.py          # Orchestrator — owns the full retry loop
    ├── agent-annotate.py       # Adds Hoare-logic contracts to a Python file
    ├── agent-reconcile.py      # Diagnoses pycsl failures → recommendation JSON
    ├── agent-script-update.py  # Applies recommendations to agent-annotate.py
    │                           #   or skill-annotate.md (never tests/annotated/)
    ├── agent-script-update-mcp.py  # MCP server enforcing write restrictions
    ├── agent-meta-evaluator.py # QA judge: syntax + pycsl re-check after each fix
    ├── agent-meta-monitor.py   # Operational watchdog: JSON failures, MCP rejections
    ├── agent-meta-reviewer.py  # LLM-generated PR description + system recommendation
    ├── skill-annotate.md       # Annotator skill/prompt (editable by update agent)
    └── agents-config.json      # Shared config (model, project-directory, …)
```

---

## How it works

```
For each .py file in tests/to_annotate/:

  ┌─────────────┐
  │ agent-      │  adds @requires / @ensures / @invariant / @variant
  │ annotate.py │  contracts to the Python script
  └──────┬──────┘
         │ annotated file → tests/annotated/
         ▼
  ┌─────────────┐
  │   pycsl     │  compiles to WhyML and runs Alt-Ergo
  └──────┬──────┘
         │ pass → next file
         │ fail ──────────────────────────────────────────────┐
         ▼                                                    │
  ┌──────────────────┐                                        │
  │ agent-reconcile  │  reads pycsl output + annotated file   │
  │ .py              │  → recommendation JSON                 │
  └──────┬───────────┘                                        │
         │                                                    │
         ▼                                                    │
  ┌──────────────────────┐                                    │
  │ agent-script-update  │  edits agent-annotate.py or        │
  │ .py                  │  skill-annotate.md via MCP         │
  └──────┬───────────────┘                                    │
         │                                                    │
         ▼                                                    │
  ┌──────────────────────┐                                    │
  │ agent-meta-evaluator │  syntax check + pycsl re-run       │
  └──────────────────────┘                                    │
         │                                                    │
         └────────────────── retry (max 10) ─────────────────┘

  After all retries for a file:
  ┌──────────────────────┐
  │ agent-meta-monitor   │  parse all attempt logs → health JSON
  └──────────────────────┘

  On halt (exit 72 or 73):
  ┌──────────────────────┐
  │ agent-meta-reviewer  │  LLM-generated PR body + recommendation
  └──────────────────────┘
```

### Inter-agent data flow

All agents communicate via **files on disk**, invoked as subprocesses by the
coordinator.

| Step | Writer | File(s) | Reader |
|------|--------|---------|--------|
| Annotate | `agent-annotate` | `tests/annotated/*.py` | `pycsl` |
| Prove | `pycsl` | `out.std`, `out.err` | `agent-reconcile` |
| Reconcile | `agent-reconcile` | `reconcile_<file>.json` | `agent-script-update` |
| Update | `agent-script-update` | modified `agent-annotate.py` or `SKILL.md`; `update_*_history.json` | coordinator (re-annotate) |
| Evaluate | `agent-meta-evaluator` | `metrics/evaluator/<stem>_<N>.json` | `agent-meta-reviewer` |
| Monitor | `agent-meta-monitor` | `metrics/monitor/<stem>.json` | `agent-meta-reviewer` |
| Review | `agent-meta-reviewer` | `metrics/reviewer/<stem>.json` + `<stem>.md` | human / CI |

All inter-agent JSON files are validated against schemas in `config/schemas/`
before being written.

### Loop detection

If `agent-reconcile` produces the **same recommendation 3 times in a row**
the coordinator halts with **exit code 73** so a human can intervene.
A report is automatically written to `metrics/reviewer/`.

### Exit codes

| Code | Meaning |
|------|---------|
| `0`  | All files passed |
| `1`  | Generic error |
| `72` | Max retries (10) exhausted for at least one file |
| `73` | Loop detected — identical recommendation 3× in a row |

---

## Class support

PyCSL supports Python classes at three levels of depth, each building on the
previous. All three are verified end-to-end by Why3/Alt-Ergo.

### Level 2 — Mutable record types

Every Python class becomes a WhyML mutable record type.  Methods receive
`(self: classname)` as their first parameter; field reads and writes lower to
plain record-field access (`self.field`) and record-update (`self.field <-
val`).

```python
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    #@ assigns self._value
    def increment(self, amount: int) -> int:
        self._value += amount
        return self._value
```

Generated WhyML:

```whyml
type counter = { mutable _value: int }

let counter__increment (self: counter) (amount: int) : int
  requires { (amount >= 0) }
  ensures  { (self._value = ((old self._value) + amount)) }
=
  self._value <- self._value + amount;
  self._value
```

**Contract syntax for methods:**

| Annotation | Meaning |
|---|---|
| `#@ requires self._field >= 0` | Precondition on a field |
| `#@ ensures self._field == \old(self._field) + n` | Post-state relates to pre-state |
| `#@ assigns self._field` | Only this field is mutated |
| `#@ assigns \nothing` | Pure read-only method |

### Level 3 — Class invariants

A `#@ class invariant <expr>` annotation placed **before** the `class` keyword
declares a property that Why3 automatically checks at every method boundary —
no extra per-method contract is needed.

```python
""  # pycsl
#@ class invariant self._value >= 0
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    #@ assigns self._value
    def increment(self, amount: int) -> int:
        self._value += amount
        return self._value
```

Generated WhyML:

```whyml
type counter = { mutable _value: int }
  invariant { _value >= 0 }
  by { _value = 0 }
```

**Invariant rules:**

| Feature | Syntax / note |
|---|---|
| Single-field | `#@ class invariant self._n >= 0` |
| Cross-field | `#@ class invariant self._lo <= self._hi` |
| Compound | `#@ class invariant self._v >= 0 and self._v <= 100` |
| Stacked | Multiple `#@ class invariant` lines — one clause per line |
| Two classes | Each class gets its own `#@ class invariant` before its `class` |
| Witness | Auto-generated from `__init__` initial values — no manual work needed |

The `by { ... }` witness proves the type is inhabited (i.e., the invariant is
satisfiable). It is derived automatically from the literal assignments in
`__init__` (e.g., `self._value = 0` → `_value = 0` in the witness).

---

## PyCSL contract language (quick reference)

| Annotation | Scope | Purpose |
|---|---|---|
| `#@ requires <expr>` | Function / method | Precondition |
| `#@ ensures <expr>` | Function / method | Postcondition; `\result` is the return value |
| `#@ assigns <targets> \| \nothing` | Function / method | Frame condition |
| `#@ \variant <expr>` | Function / method | Termination measure (recursive functions) |
| `#@ \variant (<expr>, <ordering>)` | Function / method | Termination via well-founded ordering |
| `#@ \diverges` | Function / method | Function may not terminate |
| `#@ \trusted` | Function / method | Body not verified; contracts assumed as axioms |
| `#@ loop invariant <expr>` | `while` / `for` | Inductive property |
| `#@ loop variant <expr>` | `while` / `for` | Termination measure |
| `#@ class invariant <expr>` | `class` | Type-level invariant (Level 3) |

**Operators supported in contract expressions:**
`==`, `!=`, `<`, `>`, `<=`, `>=`, `+`, `-`, `*`, `and`, `or`, `not`,
`==>` (implies), `<==>` (iff), `\result`, `\old(expr)`, `self.field`,
`\forall var; expr` (universal quantifier),
`\exists var; expr` (existential quantifier)

### Quantifiers

`\forall` and `\exists` let you write quantified properties over integer
ranges — typically array index bounds.  The bound variable is separated from
the body by a semicolon.  The variable is always typed as `int` in the
generated WhyML.

```python
# every element in [0, n) is non-negative
#@ requires \forall i; 0 <= i and i < n ==> arr[i] >= 0

# there is at least one element equal to the target
#@ ensures \exists j; 0 <= j and j < n and arr[j] == target
```

Generated WhyML:

```whyml
requires { (forall i : int. (0 <= i && i < n) -> arr[i] >= 0) }
ensures  { (exists j : int. (0 <= j && j < n) && arr[j] = target) }
```

Quantifiers may appear inside any contract expression (`requires`, `ensures`,
`loop invariant`) and can be nested.  The bound variable is excluded from
scope checking — only the free variables in the body must be in scope.

**Not supported in contracts:** `//`, `%`, `len(...)`, function calls,
`True`/`False`/`None`.

### String Literals

String literals (`"hello"`) are supported in contracts and function bodies.
Functions with `str` parameters or return types are mapped to WhyML's `string` type.

```python
#@ ensures \result == "hello"
def greet() -> str:
    return "hello"
```

---

## Usage

### Full pipeline (annotate → prove → repair loop)

```bash
./run.sh
```

### Selective function verification

```bash
# Only verify foobar and its transitive call-dependencies (e.g. double_int)
./pycsl --fun foobar myfile.py

# Verify multiple specific functions
./pycsl --fun foobar --fun helper myfile.py
```

Functions not selected (and not called by selected functions) become trusted
stubs: their contracts are assumed as axioms, but their bodies are not checked.

### Multi-file verification

PyCSL automatically resolves `from ... import ...` and `import ...` statements
to local source files. Imported functions are injected as trusted stubs
(contracts assumed, bodies not re-verified).

```bash
# file2.py contains: from dir1.file1 import double_int
./pycsl dir2/file2.py   # auto-imports double_int's contract from dir1/file1.py

# Also works with module imports:
# file3.py contains: import dir1.file1 as lib; lib.double_int(x)
./pycsl dir3/file3.py   # resolves dir1.file1, imports double_int

# Wildcard imports: from mod import *
./pycsl file_with_wildcard.py   # imports only functions actually called

# Recursive transitive resolution (A→B→C):
./pycsl --deep file.py   # resolves dependencies' own imports too
```

External modules (stdlib, third-party) are skipped — add `\trusted` stubs
manually if callers need their contracts.

### Re-run a meta-agent on existing metrics (without re-annotating)

```bash
# Re-generate the reviewer report for a file
./run.sh --review 001-basic-control-flow

# Re-run the operational health monitor for a file
./run.sh --monitor 001-basic-control-flow

# Re-run the QA evaluator for a specific annotated/modified file pair
./run.sh --evaluate 001-basic-control-flow \
    tests/annotated/001-basic-control-flow.py \
    agents/skill-annotate.md
```

The `<file-stem>` argument is the filename without extension, matching what
is stored under `metrics/`.

### Output locations

| Meta-agent | Output |
|------------|--------|
| `agent-meta-evaluator` | `metrics/evaluator/<stem>_<attempt>.json` |
| `agent-meta-monitor`   | `metrics/monitor/<stem>.json` |
| `agent-meta-reviewer`  | `metrics/reviewer/<stem>.json` + `<stem>.md` |

---

## Configuration

Edit `agents/agents-config.json` to change the LLM model or project directory:

```json
{
  "model": "claude-sonnet-4.6",
  "project-directory": "./my_project",
  "skill-annotate": "skill-annotate.md"
}
```

The update agent may only modify `agents/agent-annotate.py` or
`agents/skill-annotate.md` — writing to `tests/annotated/` is blocked by the
MCP server.

