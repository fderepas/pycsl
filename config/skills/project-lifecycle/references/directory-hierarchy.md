# Directory Hierarchy — Prescriptive Naming and Layout

This reference defines the mandatory directory structure for project
execution under the recursive five-level lifecycle. Every specification
level materializes as a directory in the filesystem. The hierarchy makes
the V-model decomposition navigable, traceable, and self-documenting.

---

## 1. Hierarchy Root

Every project has a single hierarchy root at `projects/<project>/BL/`.
`BL` stands for **Business Level** — the top of the V-model. All
specification levels nest below it.

```
projects/<project>/
├── PROJECT.md
├── BL/                         ← hierarchy root (Business Level)
│   ├── requirements/
│   ├── specifications/
│   ├── tests/
│   ├── SY1-<Name>/
│   │   └── ...
│   └── SY2-<Name>/
│       └── ...
├── docs/                       ← cross-cutting governance artifacts
│   ├── process/
│   ├── reports/
│   ├── diagrams/
│   └── audits/
├── message-queues/
└── inputs/
```

The `BL/` tree holds **all execution artifacts** — requirements,
specifications, tests, and source code. The `docs/` tree retains
**cross-cutting governance artifacts** that are not owned by a single
level (process documents, audit reports, metrics reports, RTMs).

---

## 2. Level Prefixes

| Level | Prefix | Format | Example |
|---|---|---|---|
| Business | `BL` | Fixed name, no number | `BL/` |
| System | `SY<N>` | `SY` + sequential number + `-` + PascalCase name | `SY1-PaymentGateway/` |
| Component | `CO<N>` | `CO` + sequential number + `-` + PascalCase name | `CO1-TransactionEngine/` |
| Module | `MO<N>` | `MO` + sequential number + `-` + PascalCase name | `MO1-PaymentProcessor/` |
| Unit | `UN<N>` | `UN` + sequential number + `-` + PascalCase name | `UN1-ValidateCard/` |

### Naming Rules

1. **Prefix is mandatory.** The two-letter prefix identifies the level
   unambiguously in any listing or path.
2. **Number is 1-indexed and sequential** within the parent directory.
   Numbers are assigned in the order the Specifier decomposes the parent.
3. **Name uses PascalCase** — no spaces, no underscores, no hyphens
   beyond the prefix separator. Use the domain name that the Specifier
   assigns during decomposition.
4. **`BL` has no number** — there is exactly one Business Level per project.
5. **Names must be unique** within the same parent directory.
6. **Short, descriptive names** — aim for 1–3 words. The name should
   identify the item, not describe it (that is what `specifications/main.md`
   is for).

---

## 3. Per-Directory Artifact Structure

Every level directory contains a fixed set of subdirectories:

| Subdirectory | Present At | Content | Producer |
|---|---|---|---|
| `requirements/` | All levels | Requirements for this level, derived from the parent level's specifications | Parent Specifier |
| `specifications/` | All levels | Specifications produced by the Specifier at this level | Specifier |
| `tests/` | All levels | Test plans and test results produced by the Verifier | Verifier |
| `src/` | CO, MO, UN only | Source code | Phase 10 Coder (or retro-imported) |

### File Naming Inside Subdirectories

Each subdirectory contains at least one `main.md` file:

```
SY1-PaymentGateway/
├── requirements/
│   └── main.md             ← requirements from BL specifications
├── specifications/
│   └── main.md             ← SRS / SAD / ICD / coordination spec
├── tests/
│   └── main.md             ← system test plan + results
├── src/                    ← (not present at SY level)
├── CO1-TransactionEngine/
│   └── ...
└── CO2-NotificationService/
    └── ...
```

When a single `main.md` is not sufficient (large specifications, multiple
test suites), additional files are allowed:

```
specifications/
├── main.md                 ← primary specification
├── coordination-spec.md    ← how sub-items interact
└── interface-spec.md       ← external interface details
```

```
tests/
├── main.md                 ← test plan
├── test-results.md         ← execution results
└── test_*.py               ← executable test files
```

```
src/
├── module.py               ← source files
├── __init__.py
└── helpers.py
```

---

## 4. Requirement Flow — Parent Specs Become Child Requirements

The V-model top-down flow is encoded in the directory structure:

```
BL/specifications/main.md
    ↓ (Specifier decomposes into systems)
    ↓ per-system requirements extracted into:
BL/SY1-PaymentGateway/requirements/main.md
    ↓ (System Specifier decomposes into components)
    ↓ per-component requirements extracted into:
BL/SY1-PaymentGateway/CO1-TransactionEngine/requirements/main.md
    ↓ (Component Specifier decomposes into modules)
    ↓ ...and so on down to UN level
```

**Rule:** The `requirements/main.md` at level N is a subset of the
`specifications/main.md` at level N+1 (the parent). The parent
Specifier writes both the parent's specification and the child's
requirements — they are produced in the same Synchronize step.

**Traceability:** Every requirement in `requirements/main.md` must
contain a traceable reference to the parent specification section it
was derived from. The format is: `[Traces to: <parent-path>#<section>]`.

---

## 5. Profile-Aware Truncation

The directory depth depends on the project's tailoring profile:

| Profile | Deepest Level | Directory Depth | Phase 10 Invoked From |
|---|---|---|---|
| S (Small) | SY | `BL/SY<N>-<Name>/` | System Level |
| M (Medium) | CO | `BL/SY<N>-<Name>/CO<N>-<Name>/` | Component Level |
| L (Large) | UN | `BL/SY.../CO.../MO.../UN<N>-<Name>/` | Unit Level |

**Profile S:** `src/` appears directly in each `SY<N>-<Name>/` directory.
Code is written against the L2 spec (SRS) without formal decomposition
below System level.

**Profile M:** `src/` appears in each `CO<N>-<Name>/` directory. Code
is written against the L3 spec (HLD) without per-function annotations.

**Profile L:** `src/` appears at CO, MO, and UN levels. The full
hierarchy is used.

---

## 6. Worked Example — Profile L

A project with 2 systems, each having 2 components:

```
projects/foobar/
├── PROJECT.md
├── BL/
│   ├── requirements/
│   │   └── main.md
│   ├── specifications/
│   │   └── main.md
│   ├── tests/
│   │   └── main.md
│   ├── SY1-OrderManagement/
│   │   ├── requirements/
│   │   │   └── main.md
│   │   ├── specifications/
│   │   │   └── main.md
│   │   ├── tests/
│   │   │   └── main.md
│   │   ├── CO1-OrderProcessor/
│   │   │   ├── requirements/
│   │   │   │   └── main.md
│   │   │   ├── specifications/
│   │   │   │   └── main.md
│   │   │   ├── tests/
│   │   │   │   └── main.md
│   │   │   ├── src/
│   │   │   ├── MO1-OrderValidator/
│   │   │   │   ├── requirements/
│   │   │   │   │   └── main.md
│   │   │   │   ├── specifications/
│   │   │   │   │   └── main.md
│   │   │   │   ├── tests/
│   │   │   │   │   └── main.md
│   │   │   │   ├── src/
│   │   │   │   ├── UN1-ValidateOrderItems/
│   │   │   │   │   ├── requirements/
│   │   │   │   │   │   └── main.md
│   │   │   │   │   ├── specifications/
│   │   │   │   │   │   └── main.md
│   │   │   │   │   ├── tests/
│   │   │   │   │   │   └── main.md
│   │   │   │   │   └── src/
│   │   │   │   └── UN2-CalculateTotal/
│   │   │   │       ├── requirements/
│   │   │   │       │   └── main.md
│   │   │   │       ├── specifications/
│   │   │   │       │   └── main.md
│   │   │   │       ├── tests/
│   │   │   │       │   └── main.md
│   │   │   │       └── src/
│   │   │   └── MO2-OrderPersistence/
│   │   │       └── ...
│   │   └── CO2-InventoryTracker/
│   │       └── ...
│   └── SY2-PaymentProcessing/
│       ├── requirements/
│       │   └── main.md
│       ├── specifications/
│       │   └── main.md
│       ├── tests/
│       │   └── main.md
│       ├── CO1-PaymentGateway/
│       │   └── ...
│       └── CO2-InvoiceGenerator/
│           └── ...
├── docs/
│   ├── process/
│   ├── reports/
│   ├── diagrams/
│   └── audits/
├── message-queues/
└── inputs/
```

---

## 7. Directory Creation Rules

1. **T1 (Project Initialisation):** Create `BL/` with `requirements/`,
   `specifications/`, and `tests/` subdirectories.
2. **T2 (Business Level — Synchronize step):** After the Specifier
   decomposes into systems, create one `SY<N>-<Name>/` directory per
   system with `requirements/`, `specifications/`, and `tests/`. Populate
   each system's `requirements/main.md` with the per-system requirements
   derived from the BL specification.
3. **T3 (System Level — Synchronize step):** Same pattern — create
   `CO<N>-<Name>/` directories per component under the current system.
   Add `src/` to each component directory.
4. **T4 (Component Level — Synchronize step):** Create `MO<N>-<Name>/`
   directories per module. Include `src/`.
5. **T5 (Module Level — Synchronize step):** Create `UN<N>-<Name>/`
   directories per complex unit. Include `src/`.
6. **T7 (Phase 10):** Write source code to the `src/` directory of the
   leaf level directory (the deepest level in scope per the project's
   tailoring profile).

**Rule:** Directories are created during the Synchronize step of each
level, not before. The Specifier's decomposition determines how many
subdirectories are created and what they are named.

---

## 8. Path Reference Convention

When referencing a location in the hierarchy from any skill or document,
use the full relative path from the project root:

```
BL/SY1-OrderManagement/CO1-OrderProcessor/specifications/main.md
BL/SY2-PaymentProcessing/requirements/main.md
BL/tests/main.md
```

When referencing the hierarchy pattern generically:

```
BL/SY<N>-<Name>/CO<N>-<Name>/MO<N>-<Name>/UN<N>-<Name>/
```

---

## 9. Constraints

| Rule | Requirement |
|---|---|
| No level skipping | Directories must follow the hierarchy: BL → SY → CO → MO → UN. A component cannot appear directly under BL. |
| No orphan directories | Every `SY`, `CO`, `MO`, `UN` directory must have a parent at the level above. |
| requirements/ always populated | Every non-BL level directory must have a `requirements/main.md` before specifications can be written. |
| Naming is final at creation | Renaming a directory after creation requires Change Control (cmmi-glue Workflow 2) because paths are Configuration Items. |
| Profile compliance | Do not create directories below the project's tailoring profile depth. |
