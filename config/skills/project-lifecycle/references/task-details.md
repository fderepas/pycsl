# Task Details — T2 through T6

This reference contains the detailed five-step activity descriptions for
each specification-level execution task (T2–T6). Each task follows the same
Synchronize → Delegate → Sub-actors Work → Run Tests → Reconcile cycle.
See `SKILL.md` §4 for the task summaries and orchestration rules (T7, T8).

All directory paths follow the naming convention defined in
`references/directory-hierarchy.md`.

---

## T2 — Execute Business Level

**Actors:** Business Analyst (Specifier), UAT Test Engineer (Verifier),
Reconciliator.

**Directory context:** `BL/`

**Activities:**

1. **Synchronize.** The Business Analyst and UAT Test Engineer work together.
   The Business Analyst defines business specifications (BRD, user stories,
   use cases, domain model) in `BL/specifications/main.md`, decomposes the
   business into **systems** — the distinct bounded collections that compose
   the application — and writes the **coordination spec** describing how the
   systems interact (interfaces, data flows, shared invariants). The UAT Test
   Engineer defines the business test plan (UAT scenarios, acceptance criteria)
   in `BL/tests/main.md`. The two synchronize so the test plan exercises the
   specification.

   **Directory creation:** For each system identified, the Specifier creates:
   - `BL/SY<N>-<Name>/requirements/main.md` — per-system requirements derived
     from `BL/specifications/main.md`
   - `BL/SY<N>-<Name>/specifications/` — (empty, to be populated by T3)
   - `BL/SY<N>-<Name>/tests/` — (empty, to be populated by T3)

2. **Delegate.** Work is delegated to System Level actors (T3). Each system
   identified in step 1 becomes one invocation of T3. System-level actors
   receive both the business specification and the business test plan.
3. **Sub-actors do their work.** Each System runs its own triplet cycle.
4. **Run tests.** When all System Level work is received, the UAT test plan
   is executed.
5. **Reconcile.** If tests pass, the Business Level is complete. If tests
   fail, the Reconciliator diagnoses the fault:
   - **Specifier fault:** the coordination among systems is wrong, or the
     decomposition is flawed — even if all systems individually delivered
     correct results. The Business Analyst re-does the specification.
   - **Verifier fault:** the UAT test plan contains errors. The UAT Test
     Engineer corrects the test plan.
   - **Sub-actor fault:** one or more systems did not deliver results
     conforming to their specifications. The fault propagates downward
     into the failing System's own reconciliation.

---

## T3 — Execute System Level

**⟳ Iterate once per system identified at Business Level.**

**Actors:** System Architect (Specifier), System Test Engineer (Verifier),
Reconciliator.

**Directory context:** `BL/SY<N>-<Name>/`

**Activities:**

1. **Synchronize.** The System Architect and System Test Engineer work
   together. The System Architect defines system specifications (SRS, SAD,
   ICD) in `SY<N>-<Name>/specifications/main.md`, decomposes the system
   into **components** — the modular, replaceable building blocks (libraries,
   crates, packages, services) — and writes the **coordination spec**
   (component interfaces, protocols, message orderings). The System Test
   Engineer defines the system test plan (system tests, integration tests)
   in `SY<N>-<Name>/tests/main.md`. UML use-case and sequence diagrams
   produced via `plantuml` clarify component boundaries. `spin-modeling`
   may be used to verify the coordination spec for deadlock and race
   conditions.

   **Directory creation:** For each component identified, the Specifier creates:
   - `CO<N>-<Name>/requirements/main.md` — per-component requirements derived
     from the system specification
   - `CO<N>-<Name>/specifications/` — (empty, to be populated by T4)
   - `CO<N>-<Name>/tests/` — (empty, to be populated by T4)
   - `CO<N>-<Name>/src/` — (empty, to be populated by Phase 10)

2. **Delegate.** Each component identified in step 1 becomes one invocation
   of T4 (Component Level). Component-level actors receive both the system
   specification and the system test plan.
3. **Sub-actors do their work.** Each Component runs its own triplet cycle.
4. **Run tests.** When all Component Level work is received, the system test
   plan is executed.
5. **Reconcile.** If tests pass, the System Level is complete. If tests fail,
   the Reconciliator diagnoses the fault:
   - **Specifier fault:** the coordination among components is wrong, or the
     decomposition is flawed. The System Architect re-does the specification.
   - **Verifier fault:** the system test plan contains errors. The System
     Test Engineer corrects the test plan.
   - **Sub-actor fault:** one or more components did not deliver results
     conforming to their specifications. The fault propagates downward
     into the failing Component's own reconciliation.

---

## T4 — Execute Component Level

**⟳ Iterate once per component identified at System Level.**

**Actors:** Technical Lead (Specifier), Integration Test Engineer (Verifier),
Reconciliator.

**Directory context:** `BL/SY<N>-<Name>/CO<N>-<Name>/`

**Activities:**

1. **Synchronize.** The Technical Lead and Integration Test Engineer work
   together. The Technical Lead defines component specifications (HLD,
   class diagrams, API contracts) in `CO<N>-<Name>/specifications/main.md`,
   decomposes the component into **modules** — classes or groups of related
   classes/functions — and writes the **coordination spec** (calling
   conventions, shared state, internal interfaces). The Integration Test
   Engineer defines the component test plan (integration tests at the
   component boundary) in `CO<N>-<Name>/tests/main.md`. UML class and
   component diagrams produced via `plantuml` clarify module boundaries.
   `spin-modeling` may be used to verify inter-module coordination for
   concurrency correctness.

   **Directory creation:** For each module identified, the Specifier creates:
   - `MO<N>-<Name>/requirements/main.md` — per-module requirements derived
     from the component specification
   - `MO<N>-<Name>/specifications/` — (empty, to be populated by T5)
   - `MO<N>-<Name>/tests/` — (empty, to be populated by T5)
   - `MO<N>-<Name>/src/` — (empty, to be populated by Phase 10)

2. **Delegate.** Each module identified in step 1 becomes one invocation
   of T5 (Module Level). Module-level actors receive both the component
   specification and the component test plan.
3. **Sub-actors do their work.** Each Module runs its own triplet cycle.
4. **Run tests.** When all Module Level work is received, the component
   test plan is executed.
5. **Reconcile.** If tests pass, the Component Level is complete. If tests
   fail, the Reconciliator diagnoses the fault:
   - **Specifier fault:** the coordination among modules is wrong, or the
     decomposition is flawed. The Technical Lead re-does the specification.
   - **Verifier fault:** the component test plan contains errors. The
     Integration Test Engineer corrects the test plan.
   - **Sub-actor fault:** one or more modules did not deliver results
     conforming to their specifications. The fault propagates downward
     into the failing Module's own reconciliation.

---

## T5 — Execute Module Level

**⟳ Iterate once per module identified at Component Level.**

**Actors:** Software Engineer (Specifier), Module Test Engineer (Verifier),
Reconciliator.

**Directory context:** `BL/SY<N>-<Name>/CO<N>-<Name>/MO<N>-<Name>/`

**Activities:**

1. **Synchronize.** The Software Engineer and Module Test Engineer work
   together. The Software Engineer defines module specifications (MLD:
   behaviors, methods, state management) in `MO<N>-<Name>/specifications/main.md`,
   decomposes the module into **units** — individual functions and methods —
   and writes the **coordination spec** (call graph, shared invariants between
   units). UML class and sequence diagrams produced via `plantuml` clarify
   unit interactions. The Module Test Engineer defines the module test plan
   (module-internal integration tests) in `MO<N>-<Name>/tests/main.md`.

   **Directory creation:** For each complex unit identified, the Specifier creates:
   - `UN<N>-<Name>/requirements/main.md` — per-unit requirements derived
     from the module specification
   - `UN<N>-<Name>/specifications/` — (empty, to be populated by T6)
   - `UN<N>-<Name>/tests/` — (empty, to be populated by T6)
   - `UN<N>-<Name>/src/` — (empty, to be populated by Phase 10)

2. **Delegate.** Each unit identified in step 1 becomes one invocation
   of T6 (Unit Level). Unit-level actors receive both the module
   specification and the module test plan.
3. **Sub-actors do their work.** Each Unit runs its own triplet cycle.
4. **Run tests.** When all Unit Level work is received, the module test
   plan is executed.
5. **Reconcile.** If tests pass, the Module Level is complete. If tests
   fail, the Reconciliator diagnoses the fault:
   - **Specifier fault:** the coordination among units is wrong, or the
     decomposition is flawed. The Software Engineer re-does the specification.
   - **Verifier fault:** the module test plan contains errors. The Module
     Test Engineer corrects the test plan.
   - **Sub-actor fault:** one or more units did not deliver results
     conforming to their specifications. The fault propagates downward
     into the failing Unit's own reconciliation.

---

## T6 — Execute Unit Level

**⟳ Iterate once per complex unit (function/method with >10 lines, branching
logic, non-obvious algorithm, or error handling) identified at Module Level.**

**Actors:** Software Engineer (Specifier), Unit Test Engineer (Verifier),
Reconciliator.

**Directory context:** `BL/SY<N>-<Name>/CO<N>-<Name>/MO<N>-<Name>/UN<N>-<Name>/`

**Activities:**

1. **Synchronize.** The Software Engineer and Unit Test Engineer work
   together. The Software Engineer defines the unit specification (LLD:
   algorithm pseudo-code, pre/post-conditions, invariants, error handling)
   in `UN<N>-<Name>/specifications/main.md`. A formal specification language
   such as ACSL (for Frama-C) or Pearlite (for Rust) may be used, making
   pre/post-conditions machine-checkable. The Unit Test Engineer defines the
   unit test plan (unit tests or, if formal specs are used, unit proofs with
   loop invariants) in `UN<N>-<Name>/tests/main.md`.
2. **Delegate.** Because there is no level below, delegation goes to
   **Phase 10** (T7): the Coder implements the function body in
   `UN<N>-<Name>/src/`; the Validator verifies it. Both receive the contract
   and verification expectations.
3. **Sub-actors do their work.** The Coder-Validator consensus loop operates.
4. **Run tests.** When code is delivered, the unit tests / proofs are
   executed.
5. **Reconcile.** If tests pass, the Unit Level is complete. If tests fail,
   the Reconciliator diagnoses the fault:
   - **Specifier fault:** the contract is too weak, a precondition is
     missing, or the contract is unrealizable. The Software Engineer
     re-does the specification.
   - **Verifier fault:** the unit test or proof obligation is wrong. The
     Unit Test Engineer corrects the test plan.
   - **Sub-actor fault:** the code implementation does not satisfy the
     contract. Re-delegate to Phase 10 (T7).

> **Reference impl (Profile-P).** The Coder-Validator consensus loop and this
> three-way reconcile routing are executed by `coordinator.py` over `src/pycsl/agents/`:
> Coder/Specifier = `agent-writer` (authors the `#@` contract — the deliverable IS the
> spec), Validator/Verifier = `pycsl --proof` (+ `agent-meta-evaluator` QA re-check),
> Reconciliator = `agent-reconcile` (emits `fault_class`). Routing: **sub-actor** →
> `agent-script-update` re-works the unit; **specifier** → re-decompose the file via
> `agent-splitter` (L4 escalation); **verifier** → the Rocq/Lean fallback or human.
> Role→agent map: [`competency-matrix.md`](competency-matrix.md).
