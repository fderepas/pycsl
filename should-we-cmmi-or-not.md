# Should we adopt CMMI for PyCSL?

**TL;DR — Yes, but only tailored, and never twice.** The CMMI skill set
maps cleanly onto PyCSL's `src/` topology and onto the discipline you
already enforce informally. The danger is duplication: most of what CMMI
asks for already exists in PyCSL under different names. Adopting CMMI
means *bridging* to the new vocabulary, not rebuilding from scratch.

This note recommends a profile-per-system migration, with hard caps to
keep the ceremony off the working code.

---

## 1. What CMMI is offering you

After reading the 13 skills (cmmi-* + project-lifecycle, import-existing-code,
communication, plantuml, spin-modeling, system-design-paradigms), the
substance reduces to **six concrete deliverables**:

| # | Asset | What it gives PyCSL |
|---|---|---|
| 1 | `projects/pycsl/BL/SY<N>-<Name>/.../` directory tree | A navigable physical mirror of the V-model; one folder per system, component, module, unit |
| 2 | `requirements/` ↔ `specifications/` ↔ `tests/` per level | Forces every artefact to have a parent requirement and a verifier — no orphans |
| 3 | Three tailoring profiles (S/M/L) | Pre-approved scope tiers — you don't re-negotiate ceremony per system |
| 4 | `cmmi-glue` four workflows (Tailoring, Change Control, SQA Escalation, Continuous Improvement) | A documented escalation path for the moments when an LLM agent or human disagrees |
| 5 | `cmmi-metrics-collection` + `cmmi-quantitative-mgmt` | Aggregates proof-success rates, doc-coherency hits, agent failure rates into control charts (genuinely useful for a verification toolchain) |
| 6 | `cmmi-coherency-audit` (17-lens framework audit) | A super-set of `bin/doc-coherency.py` — same shape, broader scope |

The rest (RACI matrices, ETVX preambles, document control headers,
practice-area citations) is **ceremony around** those six deliverables.
Useful for multi-person organisations; mostly overhead for a 1–2 person
project.

---

## 2. Where PyCSL stands today (the honest baseline)

Before deciding, look at what PyCSL has built that already *is* CMMI-shaped:

| CMMI concept | PyCSL's existing analogue | Status |
|---|---|---|
| Normative reference documents | `docs/pycsl-{concrete-syntax,static-semantics,translational}-reference.md` with `Status: Normative` preambles | Already in place |
| Document control & versioning | `Version: N.M` in each reference doc, paragraph-stable `test-suite/annotations.md` | Already in place |
| Coherency CI gate | `bin/doc-coherency.py --check` wired into `bin/run-reference-tests.sh` | Already in place |
| Traceability matrix | `test-suite/traceability-pycsl.md` (Ref → Test ID) | Already in place |
| Three-artefact baseline discipline | `pycsl-stdlib-coverage` (calls-english.md / calls-pycsl.md / src/pycsl_lib/ + MANIFEST.toml) | Already in place |
| Exception model contract under CCB | `pycsl-exception-model` skill + `src/pycsl/exception_model.py` (the table is treated as CI-level) | Already in place |
| UB perimeter / verification scope | `pycsl-ub-catalog` (5 categories with detection + escape annotations + corpus IDs) | Already in place |
| RAG-indexed skill library | `config/skills/` + `bin/update-rag.sh` | Already in place |
| Multi-agent orchestration | `src/pycsl/agents/coordinator.py` retry loop, meta-evaluator/monitor/reviewer | Already in place |

**Implication.** PyCSL is already practising CMMI Level 3 discipline on
the *language and pipeline*, just without the labels. The CMMI question
isn't "should we start being rigorous?" — it's "should we rename and
restructure our existing rigour to a standard vocabulary?"

---

## 3. The shape of the work — concrete sizing

`src/` today (LOC counted):

| Sub-package | Files | LOC | Natural profile |
|---|---:|---:|---|
| `src/pycsl/` | 60 | 22,897 | **L** — core compiler, soundness-critical |
| `src/pycsl_lib/` | 40 | 10,195 | **M** — stdlib stubs (TCB but mechanically thin) |
| `src/self-annotate/` | 25 | 7,754 | **M** — internal verification orchestrator |
| `src/pycsl_emit/` | 32 | 3,636 | **M** — emit pipeline |
| `src/lean2pycsl/` | 40 | 3,264 | **M** — Lean → PyCSL converter |
| `src/rocq2pycsl/` | 40 | 3,219 | **M** — Rocq → PyCSL converter |
| `src/pycsl_bridge/` | 26 | 2,862 | **S** — bridge utilities |
| `src/skill2rag/` | 9 | 792 | **S** — RAG indexer (already imported, per pilot) |
| `src/formal-semantics/` | (Rocq/Lean) | n/a | **L** — proof corpus, soundness-critical |

Profile thresholds from `tailoring-profiles.md`:

- **S**: ≤500 LOC OR 1 system / ≤3 modules / 1–2 devs / low risk → L1–L2 only
- **M**: 500–5000 LOC / 1–3 systems / 4–15 modules / 3–8 devs / moderate → L1–L3
- **L**: >5000 LOC / >3 systems / >15 modules / >8 devs / high or safety-critical → full L1–L5

PyCSL's profile axis is **mixed**: LOC and module-count push toward L for
the core; team-size pushes everything toward S; criticality (verification
toolchain producing soundness claims) pushes the core and the proof
corpus toward L. The profile thresholds are written for staffed teams,
not single-developer-with-LLM-agents projects — the *criticality* axis
should dominate.

**Recommended profile assignment** (criticality-first):

| Sub-package | Profile | Justification |
|---|---|---|
| `src/pycsl/` | L | Bug = unsound proof. Already has L4 detail in `module6_whyml/`. |
| `src/formal-semantics/` | L | Mechanised proofs; the floor of the trust chain. |
| `src/pycsl_lib/` | M (→ L over time) | Wrong stub = silent unsoundness. Coverage tooling already exists. |
| `src/pycsl_emit/` | M | Pipeline plumbing; few invariants. |
| `src/lean2pycsl/`, `src/rocq2pycsl/` | M | Round-trip converters; testable. |
| `src/self-annotate/` | M | Orchestrator over LLM agents; observable. |
| `src/pycsl_bridge/` | S | Glue. |
| `src/skill2rag/` | S | Already imported as Profile S pilot. |

---

## 4. The case **for** switching

1. **Mirror that already wants to exist.** `src/` already looks like 9
   systems. The `BL/SY<N>-<Name>/` tree gives each one a stable address
   for its requirements, spec, tests, and source — and an enforced place
   for inter-system coordination specs (today scattered across docs/).
2. **The directory hierarchy enforces what PyCSL aspires to.** Today the
   coupling between (e.g.) `pycsl-stdlib-coverage` discipline and
   `src/pycsl_lib/` is documented in skills but not structurally
   enforced. Putting `tests/` next to `src/` at every level makes
   stranded artefacts visible.
3. **`cmmi-glue` Workflow 3 (SQA Audit & Non-Compliance Escalation) is
   genuinely missing.** Today when an LLM agent annotation fails 3
   reconciliation rounds, the escalation is ad-hoc. The Workflow 3
   protocol formalises it.
4. **Quantitative management has real payoff for verification work.**
   Control charts over proof-success rate per system per week, UCL/LCL
   on agent retry counts, drift detection on Why3 wall-clock — these
   produce actionable signal. Today this lives loosely in `metrics/`.
5. **`spin-modeling` plugs a real gap.** PyCSL has a concurrent memory
   model and `ConcurrencyChecker` but no formal coordination-spec
   verification. Spin would close that loop for the concurrent corpus.
6. **`plantuml` is a strict gain.** Architecture diagrams in
   `docs/pycsl-software-architecture` would benefit from rendered UML.
7. **Profile L gives an EPG-blessed answer to "are we Level 3?"** —
   useful externally if PyCSL ever ships as a defensible toolchain.

## 5. The case **against** (or "tailor hard")

1. **You will pay for ceremony you already pay for.** Most CMMI checks
   duplicate `bin/doc-coherency.py`. If both run, you have two CIs
   reporting the same drift in different vocabularies.
2. **Document inflation.** Profile L mandates per-level `main.md`
   files. The core has ~60 module-level units in `module6_whyml/`
   alone. That's 60 × (`requirements/main.md`, `specifications/main.md`,
   `tests/main.md`) = 180 stub files at the leaf. Either they're real
   (massive write-up cost) or they're stubs (drift bait).
3. **`cmmi-coherency-audit` would flag every existing
   `pycsl-*` skill.** None of them carry §1 Document Control, §3 RACI,
   §4 ETVX. Either: (a) retrofit all 8 — high ceremony, low signal; (b)
   exempt them — undermines the coherency audit's premise.
4. **The agent pipeline assumes one set of skills.** `agent-annotate`
   does RAG retrieval from `config/skills/`. Adding 13 process-flavoured
   skills risks polluting retrieval for the contract-writer agents that
   need `pycsl-annotate`-shaped knowledge.
5. **`message-queues/` per-project is parallel infrastructure.** PyCSL's
   coordinator already manages agent state in `metrics/`. Adopting the
   `communication` skill literally means two queue substrates.
6. **The "team" axis is a single developer.** RACI matrices with one
   Responsible/Accountable column collapse to busywork.

---

## 6. Recommendation

**Go, but with three hard rules.**

### Rule 1 — Bridge, don't rebuild

Treat the existing PyCSL artefacts as the **substrate** under CMMI labels.
Concretely:

| CMMI artefact | Source (existing) | Action |
|---|---|---|
| BRD (L1 Business spec) | `README.md` + `docs/pycsl-software-architecture/SKILL.md` | Symlink or include — do not rewrite |
| SRS / SAD (L2 System) | `docs/pycsl-{concrete-syntax,static-semantics,translational}-reference.md` | Treat as L2 specifications for `SY1-PyCSL` |
| HLD (L3 Component) | `pycsl-software-architecture` skill (Module 1–6 pipeline) | One HLD per Module — already documented |
| RTM | `test-suite/traceability-pycsl.md` | Use as-is; rename only if needed |
| Doc coherency CI gate | `bin/doc-coherency.py` | Continues to run; `cmmi-coherency-audit` runs at a higher (skill-library) scope only |
| Stdlib baseline | `src/pycsl_lib/MANIFEST.toml` + `bin/stdlib-coverage.py` | Already three-artefact disciplined; declare as a CMMI baseline |
| Exception model | `src/pycsl/exception_model.py` + `pycsl-exception-model` skill | Declare as a baselined CI |
| UB perimeter | `pycsl-ub-catalog` | Declare as a CMMI process asset |

**The `import-existing-code` skill is the right entry point**, but its
deliverables collapse dramatically for systems that already have the
underlying artefacts. Most of the work is *attribution* (point CMMI at
existing files), not *generation*.

### Rule 2 — Profile-per-system, not uniform

Run `import-existing-code` separately for each `src/<package>/`, with the
profile from §3. The mandatory deliverables shrink with profile:

| Profile | Mandatory main.md files per system | Diagrams required | PlantUML | Verdict |
|---|---|---|---|---|
| S | 2 (BL spec + BL tests) | use case | optional | Cheap |
| M | 4–6 (+ SY spec/tests, + per-CO) | use case + component | yes | Moderate |
| L | 12+ (down to per-unit) | use case + component + sequence + class | yes | Expensive — reserve for core |

Apply L *only* to `src/pycsl/` and `src/formal-semantics/`. Everything
else is M or S. This is the single biggest cost lever.

### Rule 3 — CMMI skills govern process, `pycsl-*` skills govern the language

Do **not** retrofit the 8 `pycsl-*` skills to CMMI §1–§6 format. They
are *domain* skills (what to write in an annotation, how the IR maps to
WhyML), not *process* skills (how to run a project). Mixing the two
formats damages both. Instead:

- `cmmi-coherency-audit` audits `config/skills/cmmi-*/` and process
  skills against each other.
- `bin/doc-coherency.py` continues to audit `pycsl-*` skill ↔ docs ↔
  README ↔ annotations.md coherency.
- Add a short note to `cmmi-coherency-audit`'s scope: "delegates
  language-surface coherency to `bin/doc-coherency.py`."

This preserves the working RAG retrieval for annotator agents and avoids
turning every domain skill into a 400-line CMMI document.

---

## 7. What to do this week vs over a quarter

| Now (≤1 day) | Soon (≤2 weeks) | Eventually |
|---|---|---|
| Create `projects/pycsl/PROJECT.md` with profile assignments from §3 | Run `import-existing-code` against `src/skill2rag/` (Profile S — pilot already validated) | Run Profile L import against `src/pycsl/`; budget 5–10 sessions |
| Create `projects/pycsl/BL/` with `SY<N>-<Name>/` dirs (empty stubs, one per src/* subdir) | Symlink `README.md` → `BL/specifications/main.md`; the 3 reference docs into `BL/SY1-PyCSL/specifications/`; `traceability-pycsl.md` → `docs/reports/traceability-matrix.md` | Wire `cmmi-quantitative-mgmt` to consume `metrics/` outputs; chart proof-success rate per system per week |
| Decide naming for the 9 systems (suggestion: `SY1-PyCSL`, `SY2-FormalSemantics`, `SY3-PyCSLLib`, `SY4-SelfAnnotate`, `SY5-PyCSLEmit`, `SY6-Lean2PyCSL`, `SY7-Rocq2PyCSL`, `SY8-PyCSLBridge`, `SY9-Skill2RAG`) | Run `cmmi-coherency-audit` scoped to `cmmi-*` skills only; address any findings | Profile M imports for the 4 mid-tier systems |
| **Do not** delete or move any `src/<x>/` — the user's vision is explicit: code stays in `src/` | Add a section to `bin/run-reference-tests.sh` that runs `cmmi-coherency-audit` (read-only check) | Decide whether `cmmi-glue` Workflow 3 escalation supersedes the current LLM-coordinator retry loop |

---

## 8. Risks to watch

1. **Drift between `src/<x>/` and `projects/pycsl/BL/SY<N>-<Name>/`.**
   Source moves, the BL mirror doesn't. Mitigate by treating BL as
   spec-only (no copies of source), or by adding a `bin/cmmi-mirror-check.py`
   that flags missing or stale system folders against `src/`.
2. **Coherency-audit avalanche.** First framework-wide run will find
   hundreds of "missing §1 / §3 / §5" findings against the pycsl-*
   skills. Pre-tailor it (§6 of `cmmi-coherency-audit`) to exempt those
   skills before the first run, or you'll spend a day classifying
   findings you don't intend to act on.
3. **Two-substrate communication.** If you start using `message-queues/`
   for the import pilot, decide quickly whether the LLM coordinator
   migrates to it or stays on `metrics/`. Don't run both indefinitely.
4. **PlantUML staleness.** Diagrams that aren't regenerated from a
   single source of truth go stale within months. Either commit
   `.puml` sources only and render in CI, or skip the diagram
   requirement under Profile M.
5. **CCB ceremony on a 1-developer project.** Every CMMI skill ends
   with "requires Change Control Board approval per `cmmi-glue`
   Workflow 2". For PyCSL today, the CCB is one person. Pre-approve
   self-CCB in `PROJECT.md` so the workflow doesn't block edits.

---

## 9. The bottom line

CMMI is the right framing for PyCSL **because PyCSL is already most of
the way there**. The cost of adopting is mostly *attribution and
profile-tailoring*, not document generation. The two genuine wins are
(a) Workflow 3 escalation (today implicit) and (b) quantitative process
management once enough proof runs accumulate.

The trap to avoid is uniform application. Profile L on the core +
formal-semantics, Profile M on the mid-tier, Profile S on the small
utilities, and **no retrofit on the existing `pycsl-*` skills**. Bridge
existing artefacts via symlinks/includes; do not regenerate them in
CMMI ceremony format.

If you accept that envelope: start with `src/skill2rag/` (already
piloted, already imported under the previous skill version) and one
fresh Profile S import to validate the v2.0 flow, then plan the Profile
L import for `src/pycsl/` as a multi-session project on its own.

---

## 10. One question worth deciding before invoking `import-existing-code`

`projects/pycsl/` does not exist yet, and the user's vision is "code
stays in `src/`". The `import-existing-code` Phase 0 scaffolds
`BL/.../CO<N>-<Name>/src/` directories *expecting* source to move
there. Two options:

| Option | Description | Recommendation |
|---|---|---|
| **A — Spec mirror only** | `projects/pycsl/BL/SY<N>-<Name>/` holds requirements/specs/tests; `src/` stays put; no `src/` under BL | Matches user's stated vision. Requires patching `import-existing-code`'s Phase 4 P4.2 check to recognize external src location, or recording the deviation as Profile-S/M/L tailoring. |
| **B — Move source under BL** | `projects/pycsl/BL/SY1-PyCSL/.../src/` becomes the canonical home; `src/` removed or symlinked back | Cleanest mapping to `import-existing-code` as written. Big diff, lots of import paths to fix, contradicts user's stated intent. |

**Recommendation: Option A** — record it as a project-wide tailoring
deviation in `PROJECT.md`, citing `cmmi-glue` Workflow 1.

---

*Author: Claude (analysis, not yet a CMMI-baselined document).
Place this file under `projects/pycsl/docs/reports/` once the
project scaffold exists.*
