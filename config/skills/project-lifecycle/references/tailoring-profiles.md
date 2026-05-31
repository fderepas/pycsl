# Tailoring Profiles — Pre-Approved Process Right-Sizing

This reference defines three pre-approved tailoring profiles for the
project lifecycle. Selecting a profile at project bootstrap constitutes an
approved tailoring under cmmi-glue Workflow 1 (fast-track path).

*Practice area: OPD SP 1.1 — Establish Standard Processes with controlled
variation points.*

---

## Profile Selection Criteria

| Criterion        | Profile S (Small)      | Profile M (Medium)       | Profile L (Large)         |
|------------------|------------------------|--------------------------|---------------------------|
| Codebase size    | ≤ 500 LOC              | 500 – 5 000 LOC          | > 5 000 LOC               |
| Systems          | 1                      | 1 – 3                    | > 3 or monorepo           |
| Modules per sys  | ≤ 3                    | 4 – 15                   | > 15                      |
| Team size        | 1 – 2 developers       | 3 – 8 developers         | > 8 or multi-team         |
| Risk / safety    | Low                    | Moderate                 | High / safety-critical    |
| Regulatory need  | None                   | Internal compliance only | External certification    |

**Selection rule:** Choose the profile whose column matches **most** criteria.
When in doubt, choose the heavier profile. Any project may override its
profile by running the full Workflow 1 tailoring ceremony in cmmi-glue.

---

## Level Scope per Profile

```
Level / Task   Description                   Profile S   Profile M   Profile L
─────────────  ────────────────────────────  ──────────  ──────────  ──────────
Phase 1        Gap Analysis                  ✓           ✓           ✓
Phase 2        Process Documentation         ✓           ✓           ✓
T2             Business Level Execution      ✓           ✓           ✓
T3             System Level Execution        ✓           ✓           ✓
T4             Component Level Execution     —           ✓           ✓
T5             Module Level Execution        —           —           ✓
T6             Unit Level Execution          —           —           ✓
T7             Phase 10 (Code + Validate)    ✓ (direct)  ✓ (direct)  ✓
Phase 12       Final Audit                   ✓           ✓           ✓
```

> **Profile S note:** Phase 10 (T7) is invoked directly from System
> Level (T3) — code is written against the L2 spec (SRS) without formal
> L3/L4/L5 decomposition. Phase 12 (Final Audit) is scoped to L1+L2 only.

> **Profile M note:** Phase 10 (T7) is invoked directly from Component
> Level (T4) — code is written against the L3 spec (HLD) without
> per-function formal annotations. Phase 12 scope includes L1+L2+L3.

---

## Execution Diagram per Profile

### Profile S

```
  Phase 1  Gap Analysis                          Phase 12  Final Audit (L1+L2)
      ↓                                              ↑
  Phase 2  Process Docs                              │
      ↓                                              │
  T2  BUSINESS LEVEL  [Synch → Delegate → Sub-actors → Tests → Reconcile]
      │                                              │
      ├── FOR EACH SYSTEM ──────────────────────┐    │
      │                                          │    │
      │  T3  SYSTEM LEVEL  [Synch → Delegate → Sub-actors → Tests → Reconcile]
      │      │                                   │    │
      │      └── T7  PHASE 10 (leaf)             │    │
      │                                          │    │
      └──────────────────────────────────────────┘    │
      ↓                                              ↑
      └──────────────────────────────────────────────┘
```

### Profile M

```
  Phase 1  Gap Analysis                              Phase 12  Final Audit (L1–L3)
      ↓                                                  ↑
  Phase 2  Process Docs                                  │
      ↓                                                  │
  T2  BUSINESS LEVEL  [Synch → Delegate → Sub-actors → Tests → Reconcile]
      │                                                  │
      ├── FOR EACH SYSTEM ──────────────────────────┐    │
      │                                              │    │
      │  T3  SYSTEM LEVEL  [Synch → Delegate → Sub-actors → Tests → Reconcile]
      │      │                                       │    │
      │      ├── FOR EACH COMPONENT ────────────┐   │    │
      │      │                                    │   │    │
      │      │  T4  COMPONENT LEVEL  [Synch → Del → Sub → Tests → Rec]
      │      │      │                             │   │    │
      │      │      └── T7  PHASE 10 (leaf)       │   │    │
      │      │                                    │   │    │
      │      └────────────────────────────────────┘   │    │
      │                                              │    │
      └──────────────────────────────────────────────┘    │
      ↓                                                  ↑
      └──────────────────────────────────────────────────┘
```

---

## Document Scope per Profile

| Document Type             | Profile S | Profile M | Profile L |
|---------------------------|:---------:|:---------:|:---------:|
| PROJECT.md                | ✓         | ✓         | ✓         |
| BRD (Business Reqs)       | ✓         | ✓         | ✓         |
| Use cases / UAT plan      | ✓         | ✓         | ✓         |
| SRS (System Reqs)         | ✓         | ✓         | ✓         |
| SAD (Architecture)        | ✓         | ✓         | ✓         |
| Integration test plan     | ✓         | ✓         | ✓         |
| HLD (Component Design)    | —         | ✓         | ✓         |
| Component test plan       | —         | ✓         | ✓         |
| MLD (Module Design)       | —         | —         | ✓         |
| Module test plan          | —         | —         | ✓         |
| LLD (Unit Design)         | —         | —         | ✓         |
| Formal annotations        | —         | —         | ✓         |
| Unit test plan             | —         | —         | ✓         |
| Coordination specs        | ✓ (L1–L2)| ✓ (L1–L3)| ✓ (all)   |
| Reconciliation logs       | ✓ (L1–L2)| ✓ (L1–L3)| ✓ (all)   |

---

## Governance per Profile

| Aspect                    | Profile S              | Profile M              | Profile L              |
|---------------------------|------------------------|------------------------|------------------------|
| Tailoring approval        | Self-approved by PM    | EPG fast-track (auto)  | Full Wf1 ceremony      |
| Change control (Wf2)      | PM decides; no CCB     | CCB for L1–L2 changes  | Full CCB at all levels |
| SQA audit frequency       | At Phase 12 only       | At T3 completion + Phase 12 | Per cmmi-glue Wf3 |
| Continuous improvement    | Post-mortem only       | Phase 12 retro         | Full Wf4 loop          |
| Reconciliation escalation | PM handles escalations | EPG reviews escalations | Full SQA/EPG governance |

---

## Audit Scope per Profile

| Audit Phase                     | Profile S       | Profile M       | Profile L       |
|---------------------------------|:---------------:|:---------------:|:---------------:|
| A1 — Polish-skill lens          | ✓               | ✓               | ✓               |
| A2 — CMMI-documents lens        | ✓               | ✓               | ✓               |
| A3 — Agent-roles lens           | —               | ✓               | ✓               |
| A4 — CMMI-glue governance lens  | —               | —               | ✓               |
| B1 — ETVX × V-Model compat     | —               | ✓               | ✓               |
| B2 — ETVX completeness          | ✓ (L1–L2 only) | ✓ (L1–L3 only) | ✓ (all levels)  |
| C1–C3 — Cross-skill (core)      | ✓               | ✓               | ✓               |
| C4–C7 — Cross-skill (extended)  | —               | ✓               | ✓               |

---

## Recording the Profile Selection

The selected profile must be declared in `PROJECT.md` at project creation:

```markdown
## Tailoring

| Field              | Value         |
|--------------------|---------------|
| Profile            | S / M / L     |
| Justification      | (brief)       |
| Override Wf1 used  | No / Yes      |
| Approved by        | PM / EPG Lead |
```

This section is a Configuration Item (CI) — any profile change after project
start requires Change Control (cmmi-glue Workflow 2).

---

## Escalation Rules

| Condition                                         | Action                                  |
|---------------------------------------------------|-----------------------------------------|
| Project exceeds Profile S criteria during dev     | Escalate to Profile M; record in Wf2    |
| Profile M project discovers safety-critical need  | Escalate to Profile L; full Wf1 needed  |
| Profile L project de-scopes to single system      | May downgrade via Wf1 (EPG approval)    |

---

*This document is a reference artifact of the project-lifecycle skill
(SKILL-CMMI-LIFE-001) under baseline BL-LIFE-001.*
