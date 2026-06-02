# Level Definitions — Unit of Work Mapping

This reference extends the CMMI 5-level specification hierarchy (defined in
`config/skills/cmmi-process-level/references/level-definitions.md`) with a
concrete **unit of work** dimension. While `cmmi-process-level` defines what
*artifacts* belong at each level, this reference defines what *thing* is being
designed and verified at each level.

---

## Level Summary

| Level | Name | Unit of Work | Artifacts (from cmmi-process-level) | Execution Task | Directory Path |
|---|---|---|---|---|---|
| 1 | Business | The whole application | BRD, user stories, use cases, domain model, UAT plan | T2 — Business Level | `BL/` |
| 2 | System | A complete product, platform, or large subsystem composed of interacting components | SRS, SAD, ICD, integration test plan | T3 — System Level | `BL/SY<N>-<Name>/` |
| 3 | Component | A library, crate, package, or deployable service | HLD, class diagrams, API specs, component test plan | T4 — Component Level | `BL/.../CO<N>-<Name>/` |
| 4 | Module | A class or group of related classes/functions | MLD, module behaviors, module test plan | T5 — Module Level | `BL/.../MO<N>-<Name>/` |
| 5 | Unit | A single function or method | LLD, formal annotations, pre/post-conditions, unit tests | T6 — Unit Level | `BL/.../UN<N>-<Name>/` |

---

## Level 1 — Business

### Unit of Work

The **entire application** as seen by its stakeholders. There is exactly one
Level 1 per project (though the application may contain multiple systems).

### Directory

`projects/<project>/BL/` — one per project, no numbering. Contains
`requirements/`, `specifications/`, `tests/`. System subdirectories are
created as `SY<N>-<Name>/` within `BL/`.

### What Gets Designed

- Why the application exists (business goals, problem statement)
- Who uses it and how (usage requirements, personas, workflows)
- What success looks like (acceptance criteria, KPIs)
- What systems compose the application (system enumeration)
- How the systems must coordinate to deliver the outcome (coordination spec)

### What Gets Verified

- Acceptance criteria are executable (UAT scenarios)
- Each use case has a concrete expected outcome
- Every business requirement traces forward to at least one system

### Identification Rule

Ask: "Can I explain this to a non-technical stakeholder?" If yes, it is
Level 1. If it requires knowledge of architecture, APIs, or algorithms,
it belongs at a lower level.

### Iteration

No iteration — T2 executes once per project.

---

## Level 2 — System

### Unit of Work

A **bounded collection of interacting elements** that work together to
achieve a specific overarching role within the project. Concrete forms
include a complete product, a platform, or a large subsystem with its own
operational identity.

### Directory

`BL/SY<N>-<Name>/` — e.g., `BL/SY1-PaymentGateway/`, `BL/SY2-AdminPortal/`.
Contains `requirements/`, `specifications/`, `tests/`. Component
subdirectories are created as `CO<N>-<Name>/` within the system directory.

### How to Identify Systems

1. Look for distinct functional roles: each System serves a specific
   overarching purpose within the project.
2. If the project has a single purpose, it is one System.
3. If the project has multiple independent functional domains, each is a
   System.
4. A System may also be identified by deployment boundary or independent
   lifecycle.

### What Gets Designed

- Functional requirements (what the system does)
- Non-functional requirements (performance, reliability, security)
- Architecture (blocks, data flow, technology stack)
- External interfaces (APIs, file formats, protocols)
- Component decomposition (enumeration of components)
- Coordination spec: how the components interact (interfaces, protocols,
  message orderings, shared invariants)

### What Gets Verified

- End-to-end scenarios validate SRS requirements
- Integration tests verify component assembly
- Interface contracts are honoured

### Iteration

T3 iterates **once per system** identified in T2.

### Example

For skill2rag:
- **System 1:** The RAG pipeline (chunking, embedding, indexing, retrieval)
- **System 2:** The LLM client (multi-backend dispatch)

---

## Level 3 — Component

### Unit of Work

A **modular, replaceable building block** of a System. It encapsulates its
internal workings and interacts with other Components strictly through
well-defined interfaces. Concrete forms include a library, a crate in Rust,
a package in Java or Python, or a deployable service.

### Directory

`BL/SY<N>-<Name>/CO<N>-<Name>/` — e.g., `BL/SY1-PaymentGateway/CO1-TransactionEngine/`.
Contains `requirements/`, `specifications/`, `tests/`, and `src/`. Module
subdirectories are created as `MO<N>-<Name>/` within the component directory.

### How to Identify Components

1. Look for package manifests: `pyproject.toml`, `Cargo.toml`, `go.mod`,
   `package.json`, `CMakeLists.txt`.
2. If a single manifest covers the whole system, the system is one component.
3. If the system has multiple manifests (monorepo), each is a component.
4. Logical subsystems within a single package (e.g., `src/skill2rag/tools/`)
   may be treated as separate components if they have independent interfaces
   and could be extracted into their own package.

### What Gets Designed

- Component contract: the behavior it provides and the interface through
  which it does so
- Use cases for callers of the component
- API, message protocol, or interface specification
- Module decomposition (enumeration of modules within the component)
- Coordination spec: calling conventions and shared state between modules

### What Gets Verified

- Component integration tests validate the interface against the contract
- Boundary conditions are tested at the component boundary
- Interface contracts are exercised

### Iteration

T4 iterates **once per component** identified in T3.

### Example

For skill2rag core system:
- `chunker` component — markdown section-based chunking
- `embedder` component — vector embedding via Ollama
- `indexer` component — index builder
- `retriever` component — cosine-similarity search
- `cli` component — command-line interface

---

## Level 4 — Module

### Unit of Work

A **class, a small set of related classes, or a group of related free
functions** within a Component. A Module defines the shared attributes,
behaviors, and relationships of a coherent set of objects or functions.

### Directory

`BL/.../CO<N>-<Name>/MO<N>-<Name>/` — e.g., `BL/SY1-PaymentGateway/CO1-TransactionEngine/MO1-OrderValidator/`.
Contains `requirements/`, `specifications/`, `tests/`, and `src/`. Unit
subdirectories are created as `UN<N>-<Name>/` within the module directory.

### How to Identify Modules

1. List the source files in the component's directory.
2. Each file (or cohesive group of files) with public classes, functions,
   or exports is a module.
3. `__init__.py` files that only re-export are not separate modules.
4. Test files (`test_*.py`) are not modules — they are verification artifacts.

### What Gets Designed

- Module responsibility and the behaviors it provides
- Classes, dataclasses, and their relationships
- Public function/method signatures with types
- Use cases for callers of the module
- Unit decomposition (enumeration of functions/methods)
- Coordination spec: call graph and shared invariants between units

### What Gets Verified

- Module tests validate each module's public behavior
- Internal integration tests exercise coordination between units
- Boundary conditions and error paths are tested

### Iteration

T5 iterates **once per module** identified in T4.

### Example

For the `chunker` component:
- `ChunkProcessor` module — heading parsing, stack management, chunking logic
- `FileWalker` module — recursive glob + directory traversal
- `ChunkIdentifier` module — ID generation, content hashing

---

## Level 5 — Unit

### Unit of Work

A **single function or method**. This is the leaf of the level hierarchy:
there is no level below. It is the atomic unit of code — the smallest thing
that can be independently specified and verified.

### Directory

`BL/.../MO<N>-<Name>/UN<N>-<Name>/` — e.g., `BL/SY1-PaymentGateway/CO1-TransactionEngine/MO1-OrderValidator/UN1-ValidateCard/`.
Contains `requirements/`, `specifications/`, `tests/`, and `src/`. This is
the leaf level — no subdirectories are created below.

### How to Identify Units

1. List all public and private functions/methods in the module.
2. Classify each as **complex** or **simple**:
   - **Complex:** >10 lines, branching logic (if/else, loops), non-obvious
     algorithm, error handling, external API calls. → Needs full LLD.
   - **Simple:** ≤10 lines, no branching, getter/setter, pass-through,
     trivial computation. → Docstring is sufficient.
3. Only complex units iterate through T6.

### What Gets Designed

- The action the function performs
- Inputs and outputs — arguments, return values, side effects
- Pre-conditions, post-conditions, invariants
- Algorithm pseudo-code or step-by-step logic
- Error handling strategy
- Optionally: formal specification (ACSL for Frama-C, Pearlite for Rust)

### What Gets Verified

- Unit tests verify pre/post-conditions
- Boundary conditions and error paths are tested
- Property-based tests where applicable
- Formal proofs for critical algorithms (optional)
- Coverage target (>80% line coverage)

### Iteration

T6 iterates **once per complex unit** identified in T5.

### Phase 10 Delegation

Because there is no level below, delegation goes to **Phase 10 actors**:
- The **Coder** implements the function body to satisfy the contract.
- The **Validator** confirms the implementation satisfies the contract
  (runs tests, proofs, or formal verification).
The Coder receives both the contract (from the Specifier) and the
verification expectations (from the Verifier).

### Example

For `ChunkProcessor` module:
- `chunk_file()` — complex (heading parsing, stack management, 50+ lines) → LLD
- `chunk_directory()` — simple (recursive glob + delegation) → docstring only
- `_make_chunk_id()` — simple (string concatenation) → docstring only
- `_content_hash()` — simple (sha256 one-liner) → docstring only

---

## Cross-Level Traceability

Every item at one level must trace to at least one item at the adjacent
levels. This traceability serves two purposes: (1) "why does this exist?"
traces upward; (2) "where is this satisfied?" traces downward. Without
traceability, the levels become parallel checklists rather than a linked
hierarchy, and reconciliation has no path to follow when escalation across
levels is needed.

At each level, the Reconciliator ensures fault attribution is properly
recorded when tests fail:

```
Level 1 (T2): BL/specifications/main.md → BR-01 (Skill Ingestion)
    ↓ traces to          ← Reconciliator: fault attribution if Business tests fail
Level 2 (T3): BL/SY1-RagPipeline/specifications/main.md → SRS-FR-01
    ↓ traces to          ← Reconciliator: fault attribution if System tests fail
Level 3 (T4): .../CO1-Chunker/specifications/main.md → HLD-chunker-01
    ↓ traces to          ← Reconciliator: fault attribution if Component tests fail
Level 4 (T5): .../MO1-ChunkProcessor/specifications/main.md → MLD-ChunkProcessor-01
    ↓ traces to          ← Reconciliator: fault attribution if Module tests fail
Level 5 (T6): .../UN1-ChunkFile/specifications/main.md → LLD-chunk_file
    ↓ traces to          ← Reconciliator: fault attribution if Unit tests fail
Phase 10 (T7): .../UN1-ChunkFile/src/chunker.py::chunk_file()
    ↓ verified by
Tests: .../UN1-ChunkFile/tests/main.md → test_chunk_file_splits_by_heading()
```

The Requirements Traceability Matrix (RTM) in Phase 12 captures all these
links in a single document. Reconciliation logs at each level are included
as supplementary evidence in the RTM.

---

## Cross-Level Reconciliation Routing

A sub-actor fault at level N triggers reconciliation at level N−1.
Sometimes the right answer at N−1 is itself "Specifier fault" — meaning
level N−1's spec was wrong, which means level N's coordination spec for
the sub-actors was misaligned with what they could deliver. In that case
the fault escalates back up to level N. The Reconciliator at each level
must be willing to recognize this case and push back upward when warranted.

```
Level N:  test fails → Reconciliator → "sub-actor fault" → delegate down
Level N−1: sub-actor investigates → "Specifier fault at N−1"
              → escalates back to Level N (coordination spec was wrong)
Level N:  Specifier revises coordination spec → cycle resumes
```

**Reference impl (Profile-P, L5→L4).** This routing is mechanized in the annotation
`coordinator.py`. The Unit (L5) is a function; the Module (L4) is the file. When
`agent-reconcile` classifies a unit failure as `fault_class: specifier` (the file's
decomposition / callee-contract ordering is wrong, not this unit's body), the
coordinator re-decomposes the file via `agent-splitter` (the L4 actor) rather than
re-patching the unit — the concrete "escalate to N−1, revise the coordination spec"
step. A per-file `MAX_REDECOMPOSE` cap bounds L5↔L4 ping-pong, halting via exit 73
with a Workflow-3 NCR. See [`competency-matrix.md`](competency-matrix.md).
