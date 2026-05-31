# Workflow-to-Message-Type Mapping

This reference maps the four governance workflows defined in
`config/skills/cmmi-glue/references/workflow-catalog.md` to concrete message
types used in the communication protocol.

## How to Use This File

1. Determine which cmmi-glue workflow the communication relates to.
2. Look up the corresponding message `type` value in the table below.
3. Add the `type` field (and any required optional fields) to the message JSON.
4. Follow the send procedure in the communication SKILL.md (Task T5).

---

## Message Type Catalog

### Workflow 1 — Tailoring Process

| Message Type (`type` value) | Sender Role | Receiver Role | Purpose | Required Optional Fields |
|---|---|---|---|---|
| `tailoring-request` | Project Manager | EPG | Submit a request to tailor the standard framework for a project | `priority` |
| `tailoring-review` | EPG | SQA Auditor | Request SQA review of the proposed tailoring | — |
| `tailoring-decision` | EPG | Project Manager | Communicate approval or rejection of the tailoring request | `severity` (`info` = approved, `warning` = rejected with feedback) |
| `tailoring-baseline` | Configuration Manager | Project Manager, EPG | Confirm the tailored PMP has been baselined | — |

### Workflow 2 — Change Control

| Message Type (`type` value) | Sender Role | Receiver Role | Purpose | Required Optional Fields |
|---|---|---|---|---|
| `change-request` | Business Analyst | Configuration Manager | Submit a change request | `change_request_id`, `priority` |
| `change-impact-analysis` | Business Analyst | Configuration Manager | Deliver the impact analysis for a CR | `change_request_id`, `attachments` |
| `ccb-schedule` | Configuration Manager | CCB Members | Schedule a CCB meeting for CR review | `change_request_id` |
| `ccb-decision` | Configuration Manager | Business Analyst, affected roles | Communicate the CCB's decision (approve/reject/defer) | `change_request_id`, `severity` |
| `baseline-unlock` | Configuration Manager | Affected specifiers | Notify that baselines are unlocked for updates | `change_request_id` |
| `baseline-relock` | Configuration Manager | All affected roles | Confirm all artifacts are re-baselined and CR is closed | `change_request_id` |

### Workflow 3 — SQA Audit & Non-Compliance Escalation

| Message Type (`type` value) | Sender Role | Receiver Role | Purpose | Required Optional Fields |
|---|---|---|---|---|
| `audit-finding` | SQA Auditor | Engineering Role | Report a positive or negative audit finding | `severity` |
| `ncr` | SQA Auditor | Engineering Role | Issue a Non-Compliance Report | `ncr_id`, `severity` |
| `ncr-acknowledgement` | Engineering Role | SQA Auditor | Acknowledge receipt of the NCR | `ncr_id`, `in_reply_to` |
| `corrective-action-plan` | Engineering Role | SQA Auditor | Submit the corrective action plan | `ncr_id`, `in_reply_to` |
| `ncr-escalation` | SQA Auditor | Upper Management / EPG | Escalate an unresolved NCR | `ncr_id`, `severity` (`critical`) |
| `ncr-closure` | SQA Auditor | Engineering Role | Confirm the NCR is resolved and closed | `ncr_id` |

### Workflow 4 — Continuous Improvement Loop

| Message Type (`type` value) | Sender Role | Receiver Role | Purpose | Required Optional Fields |
|---|---|---|---|---|
| `metrics-report` | Metrics Analyst | EPG | Deliver a process performance report | `attachments` |
| `improvement-proposal` | EPG | Configuration Manager | Propose a process update based on metrics findings | `priority` |
| `process-update` | EPG | All agents | Announce an update to standard processes or templates | `attachments` |
| `pal-baseline` | Configuration Manager | EPG, SQA Auditor | Confirm updated process assets are baselined | — |

---

## General-Purpose Message Types

These types are not tied to a specific governance workflow but follow the
same schema and protocol:

| Message Type (`type` value) | Purpose | Typical Use |
|---|---|---|
| `task-assignment` | Assign a work item to an agent | Project Manager → any agent |
| `task-status` | Report progress on an assigned task | Any agent → Project Manager |
| `information-request` | Request information from another agent | Any agent → any agent |
| `information-response` | Respond to an information request | Any agent → any agent |
| `review-request` | Request a peer review of an artifact | Any agent → reviewer agent |
| `review-response` | Deliver review findings | Reviewer → requesting agent |

---

## Valid `type` Values Summary

All valid values for the `type` field, sorted alphabetically:

```
audit-finding
baseline-relock
baseline-unlock
ccb-decision
ccb-schedule
change-impact-analysis
change-request
corrective-action-plan
improvement-proposal
information-request
information-response
metrics-report
ncr
ncr-acknowledgement
ncr-closure
ncr-escalation
pal-baseline
process-update
review-request
review-response
tailoring-baseline
tailoring-decision
tailoring-request
tailoring-review
task-assignment
task-status
```

Total: 26 message types (20 governance + 6 general-purpose).
