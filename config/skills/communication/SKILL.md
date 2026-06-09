---
name: communication
description: >-
  Defines the file-based asynchronous messaging protocol for inter-agent
  communication. Covers message-queue initialisation, message sending with
  atomic writes, message receiving and processing, governance-workflow message
  mapping, and archive management. Use this skill whenever agents must
  exchange structured messages within a project, when setting up a
  message-queues directory, when defining message types for CMMI governance
  workflows, or when auditing message integrity.
document_id: SKILL-CMMI-COMM-001
version: "1.0"
status: Approved
effective_date: "2025-07-25"
baseline_id: BL-COMM-001
cmmi_version: "2.0"
practice_areas:
  - "CM SP 1.1 — Identify Configuration Items"
  - "OPD SP 1.1 — Establish Standard Processes"
  - "PQA SP 1.1 — Objectively Evaluate Processes"
---

# Inter-Agent Communication Protocol

## 1. Document Control & Metadata

| Field | Value |
|---|---|
| Document ID | SKILL-CMMI-COMM-001 |
| Version | 1.0 |
| Status | Approved |
| Effective Date | 2025-07-25 |
| Baseline ID | BL-COMM-001 |
| CMMI Version | 2.0 |

### Revision History

| Version | Date | Author | Change Summary |
|---|---|---|---|
| 0.1 | 2025-07-25 | Agent (EPG) | Initial draft — converted from message-spec.md |
| 1.0 | 2025-07-25 | Agent (EPG) | First approved release: full §1–§6, ETVX, RACI, metrics |

### Approvals

| Role | Name | Date | Signature |
|---|---|---|---|
| Accountable — EPG Lead | _(pending)_ | | |
| Responsible — Configuration Manager | _(pending)_ | | |

---

## 2. Introduction & Context

### Purpose

This skill defines a decentralised, asynchronous, file-based messaging
protocol that enables autonomous agents to communicate within a project.
It satisfies CMMI v2.0 practice areas CM SP 1.3 (Create or Release
Baselines — message artifacts are CIs) and OPD SP 1.1 (Establish Standard
Processes — the protocol is a standard inter-agent interface).

### Scope

| In Scope | Out of Scope |
|---|---|
| Message-queue directory initialisation; JSON message schema | Real-time streaming; binary payloads |
| Send/receive operations; atomic-write protocol | Network-based transport; encryption at rest |
| Governance-workflow message types; archive management; message integrity auditing | Message routing beyond filesystem directories |

### Audience

All agents that participate in inter-agent communication within a project.
Configuration Managers responsible for baselining message artifacts. SQA
Auditors verifying message-protocol compliance.

### References & Definitions

| Term | Definition |
|---|---|
| Message Queue | A filesystem directory (`message-queues/<agent>/`) serving as an agent's inbox |
| Atomic Write | Write to a `.tmp` file then rename — guarantees no partial reads on POSIX systems |
| ICD | Interface Control Document — the project-specific instantiation of this skill |
| Governance Message | A message whose `type` field maps to a cmmi-glue workflow (Tailoring, Change Control, SQA Audit & Non-Compliance Escalation, Continuous Improvement) |

### References

| Reference | Location |
|---|---|
| Message schema — JSON schema and field semantics for inter-agent messages. | `references/message-schema.md` |
| Workflow message mapping — Governance message types mapped to `cmmi-glue` workflows. | `references/workflow-message-mapping.md` |

### Referenced Skills

| Skill | Relationship |
|---|---|
| `agent-project-structure` | Defines where `message-queues/` lives within a project |
| `cmmi-glue` | Defines the 4 governance workflows that map to governance message types |
| `cmmi-documents` | Template for the ICD generated from this skill |
| `cmmi-agent-roles` | Defines the roles that send/receive governance messages |

---

## 3. RACI Matrix

*Practice area: OPD SP 1.1 — role-to-task mapping for the communication process.*

| Activity | Agent (any)² | Configuration Manager | EPG Lead | Project Manager | Sending Agent² | Receiving Agent² | SQA Auditor | All agents¹ |
|---|---|---|---|---|---|---|---|---|
| Initialise message-queues directory | R | A | C | I | — | — | — | — |
| Validate message schema before send | — | — | — | — | R, A | — | — | — |
| Send message (atomic write) | — | — | — | — | R, A | I | — | — |
| Receive and process message | — | — | — | — | — | R, A | — | — |
| Mark message as read | — | — | — | — | — | R, A | — | — |
| Archive processed messages | R | A | — | — | — | — | — | — |
| Purge expired archives | — | R, A | — | — | — | — | C | — |
| Audit message integrity | — | C | I | — | — | — | R, A | — |
| Map governance workflow to message type | — | C | R, A | — | — | — | — | I |
| Send governance message (T5) | — | C | I | — | R, A | — | I | — |

¹ Broadcast notification pattern — not a single persona.
² *Abstract runtime roles.* Agent (any) = any persona performing shared queue-maintenance tasks. Sending Agent = the persona initiating communication; Receiving Agent = the persona receiving. At invocation time, these bind to concrete personas from `config/agents/`. See `cmmi-agent-roles` for the resolution rules.

---

## 4. Process Architecture (Extended ETVX Model)

*Practice areas: OPD SP 1.1 — defines the standard communication process;
CM SP 1.3 — governs message-artifact storage and traceability.*

### E — Entry Criteria

All conditions must evaluate to true before an agent begins communication:

- [ ] The project's `message-queues/` directory exists at `projects/<project>/message-queues/`.
- [ ] The sending agent knows the target agent's name (the `to` field).
- [ ] The message content conforms to the mandatory JSON schema defined in `references/message-schema.md`.
- [ ] The sending agent has write access to the target agent's inbox directory.

### I — Inputs & Sources

| Input | Source | Format |
|---|---|---|
| Project name | User / project charter | Text (resolves to `projects/<project>/message-queues/`) |
| Target agent name | RACI matrix / workflow context | Text |
| Message payload | Agent logic / governance workflow | JSON (see `references/message-schema.md`) |
| Message schema | `references/message-schema.md` | Markdown (JSON schema definition) |
| Governance workflow mapping | `references/workflow-message-mapping.md` | Markdown table |

### T — Tasks / Activities

The agent executes the following steps:

#### T1 — Initialise Message Queues (once per project setup)

1. Create the directory `projects/<project>/message-queues/` if it does not exist.
2. For each agent that will participate, create a subdirectory: `projects/<project>/message-queues/<agent-name>/`.
3. Create an `archive/` subdirectory inside each agent inbox: `projects/<project>/message-queues/<agent-name>/archive/`.
4. Record the initialisation in the project's CM log.

#### T2 — Send a Message

> **Timing rule:** Send phase-handoff messages at the moment of handoff —
> not retroactively. Each phase boundary (e.g., Phase 1→2, Phase 2→3)
> must produce a communication log entry before the receiving phase begins.

1. Identify the target agent name (`to` field).
2. Construct the JSON payload with all mandatory fields (`from`, `to`, `date`, `read`, `message`). Set `read` to `false`.
3. Generate the filename: `YYYYMMDD_HHMMSSmmm_<sender>.json` (millisecond precision, UTC).
4. Write the payload to a temporary file: `projects/<project>/message-queues/<to>/<filename>.tmp`.
5. Validate the temporary file against the mandatory schema (all 5 fields present, correct types).
6. Rename `<filename>.tmp` to `<filename>` (atomic on POSIX filesystems).
7. If the rename fails, retry once after 100ms. If retry fails, log an error and do not send.

#### T3 — Receive and Process Messages

1. Scan the agent's own inbox: `projects/<project>/message-queues/<own-name>/`.
2. List all `.json` files (exclude `.tmp` files — those are in-flight writes).
3. Sort files lexicographically by filename (this gives chronological order due to the timestamp convention).
4. For each file where `"read": false`:
   a. Parse the JSON payload.
   b. Process the message content according to the agent's role and responsibilities.
   c. Update the file: set `"read": true` and add `"read_date": "<ISO 8601 UTC>"`.
   d. Write the updated JSON back using the atomic-write protocol (write to `.tmp`, rename).

#### T4 — Archive Processed Messages

1. Move files where `"read": true` to `projects/<project>/message-queues/<own-name>/archive/`.
2. Archive after all unread messages have been processed (do not archive mid-batch).
3. Retain archived messages for the duration of the project (do not delete).

#### T5 — Send Governance Messages

1. Determine which cmmi-glue workflow the message relates to (see `references/workflow-message-mapping.md`).
2. Add the `type` field to the JSON payload with the governance message type defined in `references/workflow-message-mapping.md`.
3. Add any workflow-specific optional fields (e.g., `ncr_id`, `change_request_id`, `severity`).
4. Follow the T2 send procedure.

#### Writing Constraints

| Rule | Requirement |
|---|---|
| No Conversational Prose | Messages use structured JSON. Human-readable summaries go in the `message` field only. |
| Atomic Writes | All file writes use write-to-tmp-then-rename. No direct overwrites. |
| Schema Validation | Every message is validated against the mandatory schema before send. |
| Filename Determinism | Filenames use `YYYYMMDD_HHMMSSmmm_<sender>.json` — no UUIDs, no random components. |

### V — Verification & Validation

*Practice area: PQA SP 1.1 — objective evaluation of communication-protocol adherence.*

Before marking a communication task as complete, verify all of the following:

- [ ] The `message-queues/` directory exists at the project-level path (`projects/<project>/message-queues/`).
- [ ] Every participating agent has a dedicated inbox subdirectory with an `archive/` subfolder (unless tailored per §6).
- [ ] All sent messages contain the 5 mandatory fields (`from`, `to`, `date`, `read`, `message`) (unless tailored per §6).
- [ ] All filenames follow the `YYYYMMDD_HHMMSSmmm_<sender>.json` convention (unless tailored per §6).
- [ ] No `.tmp` files remain in any inbox (all writes completed atomically).
- [ ] All processed messages have `"read": true` and a valid `read_date`.
- [ ] Governance messages include a valid `type` field from the workflow-message-mapping reference (unless tailored per §6).
- [ ] Archived messages are in the correct `archive/` subdirectory and have not been deleted (unless tailored per §6).
- [ ] No message file has been overwritten (filenames are unique by timestamp + sender, unless tailored per §6).

### X — Exit Criteria

- [ ] All V — Verification & Validation checks pass.
- [ ] The message exchange achieves a binary verifiable outcome (response file exists, workflow step record created).
- [ ] The Accountable role has confirmed completion.

### O — Outputs & Destinations

| Output | Format | Destination |
|---|---|---|
| Sent message files | JSON | `projects/<project>/message-queues/<target-agent>/` |
| Read-marked message files | JSON | `projects/<project>/message-queues/<own-agent>/` |
| Archived messages | JSON | `projects/<project>/message-queues/<own-agent>/archive/` |
| ICD (project-specific spec) | Markdown | `projects/<project>/BL/SY<N>-<Name>/specifications/icd-comm-001.md` |
| Message integrity audit report | Markdown | `projects/<project>/docs/audits/` |

**Configuration Item declaration:** Sent message files and ICD documents
are Configuration Items (CIs) under baseline `BL-COMM-001`. Changes to the
message schema or ICD require Change Control Board approval per `cmmi-glue`
Workflow 2.

---

## 5. Measurement and Metrics

*Practice area: MPM SP 1.1 — quantitative tracking of communication effectiveness.*

| KPI | Formula | Collection Point | Organisational Objective |
|---|---|---|---|
| Message delivery rate | (messages successfully renamed from .tmp) / (total send attempts) × 100 | Agent send logs | Ensure reliable inter-agent communication (>99% delivery) |
| Message processing latency | time(read_date) − time(date) | Message JSON fields | Maintain responsive agent collaboration (<5 min median latency) |
| Unread message backlog | count of files where `read: false` per inbox | Inbox directory scan | Prevent communication bottlenecks (backlog <10 per agent) |
| Schema validation failure rate | (schema validation failures) / (total send attempts) × 100 | Agent validation logs | Enforce protocol compliance (<1% failure rate) |
| Governance message ratio | (messages with `type` field) / (total messages) × 100 | Message file scan | Track governance workflow adoption (>20% for active projects) |

### Governance Review Cadence

The Metrics Analyst reviews communication KPIs once per sprint (or once per
2-week cycle for projects without sprints). Findings feed into cmmi-glue
Workflow 4 (Continuous Improvement Loop).

### Metric Collection Path

All communication metrics are collected from:
- Message delivery rate + schema validation failures: agent send logs and
  validation output under `projects/<project>/message-queues/`.
- Message processing latency: computed from `date` and `read_date` fields in
  message JSON files.
- Unread message backlog: inbox directory scan at collection time.
- Governance message ratio: message file scan across all queues.

The Metrics Analyst aggregates communication KPIs per sprint. Trends feed
into `cmmi-glue` Workflow 4 (Continuous Improvement).

---

## 6. Tailoring Guidelines

*Practice area: OPD SP 1.1 — controlled adaptation of the communication protocol.
All deviations follow `cmmi-glue` Workflow 1 (Tailoring Process).*

| Deviation | Conditions for Approval | Approval Authority |
|---|---|---|
| Omit governance message types | Project is Level 1 only (no formal governance workflows) | EPG Lead |
| Reduce archive retention | Project duration < 1 month and message volume < 100 | Configuration Manager |
| Use UUID instead of timestamp filenames | Multiple agents share the same system clock with <1ms resolution | EPG Lead |
| Skip schema validation on send | Development/prototyping phase only; must re-enable before Level 2 audit | SQA Auditor |
| Omit `archive/` subdirectory | Single-sprint projects with <50 total messages | Configuration Manager |
| **Profile-P (PyCSL): bridge-then-sunset** | The existing `metrics/logs/` tree from `coordinator.py` + meta-agents is the primary message substrate. Phase 1: `bin/cmmi-msg-bridge.py` one-way mirrors `metrics/logs/` → `projects/pycsl/message-queues/<agent>/inbox-from-logs/` with `source_uri` pointers (no content duplication). Phase 2: `agent-feature-supervisor.py` reads exclusively from the queue. Phase 3: retire dual-write; `metrics/logs/` becomes a derived view. Until Phase 2 lands, governance message types are bridged but not authored fresh into the queue. The 2026-05-31 13:47:22 `itertools.cycle` L3-ceiling message is the canonical regression-test payload that should trigger Reconciliator escalation once Phase 2 is wired. | Developer (single-developer CCB) |

All tailoring deviations must be recorded in the project's `PROJECT.md`
under a "Tailoring Deviations" section, with reference to this skill
(SKILL-CMMI-COMM-001) and the approving authority's sign-off.

---

*This document is a Configuration Item (CI) under baseline BL-COMM-001.
Changes require Change Control Board approval per cmmi-glue Workflow 2.*
