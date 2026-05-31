# Message Schema Reference

This reference defines the canonical JSON schema for inter-agent messages,
the filename convention, the atomic-write protocol, and validation rules.

## 1. Mandatory Fields

Every message file must contain exactly these five top-level fields, in this
order:

```json
{
  "from":    "<string> — sender agent name (must match a config/agents/ persona)",
  "to":      "<string> — receiver agent name (must match a config/agents/ persona)",
  "date":    "<string> — send timestamp in ISO 8601 UTC: YYYY-MM-DDTHH:MM:SS.mmmZ",
  "read":    false,
  "message": "<string> — core message content (plain text or markdown)"
}
```

### Field Constraints

| Field | Type | Constraints |
|---|---|---|
| `from` | string | Non-empty. Must correspond to an agent name in `config/agents/`. |
| `to` | string | Non-empty. Must correspond to an agent name in `config/agents/`. |
| `date` | string | ISO 8601 with milliseconds, UTC timezone. Example: `2025-07-25T14:30:00.123Z`. |
| `read` | boolean | Must be `false` on send. Set to `true` by the receiver after processing. |
| `message` | string | Non-empty. Contains the payload. May include markdown formatting. |

## 2. Optional Fields

Additional fields may be appended **below** the mandatory fields. The schema
is open-ended to support workflow-specific metadata.

### Standard Optional Fields

| Field | Type | Purpose | Used By |
|---|---|---|---|
| `type` | string | Governance message type (see workflow-message-mapping.md) | Governance workflows |
| `read_date` | string | ISO 8601 UTC timestamp when the message was read | Receiver agent |
| `priority` | string | `low`, `normal`, `high`, `critical` | Any agent |
| `in_reply_to` | string | Filename of the message being replied to | Any agent |
| `ncr_id` | string | Non-Compliance Report identifier | SQA Audit workflow |
| `change_request_id` | string | Change Request identifier | Change Control workflow |
| `severity` | string | `info`, `warning`, `error`, `critical` | SQA Audit workflow |
| `attachments` | array of strings | Relative paths to attached files within the project | Any agent |
| `task_id` | string | Identifier for the task this message relates to | Any agent |

## 3. Filename Convention

```
YYYYMMDD_HHMMSSmmm_<sender>.json
```

| Component | Format | Example |
|---|---|---|
| Date | `YYYYMMDD` | `20250725` |
| Time | `HHMMSS` | `143000` |
| Milliseconds | `mmm` | `123` |
| Sender | Agent name (kebab-case) | `sqa-auditor` |
| Extension | `.json` | `.json` |

**Full example:** `20250725_143000123_sqa-auditor.json`

### Uniqueness Guarantee

The combination of millisecond-precision timestamp and sender name ensures
uniqueness under normal operating conditions. If two messages from the same
sender occur within the same millisecond, the second send must wait 1ms
before generating its filename.

### Temporary File Convention

During atomic writes, the temporary file uses the same name with a `.tmp`
suffix appended:

```
20250725_143000123_sqa-auditor.json.tmp
```

Consumers must ignore all `.tmp` files when scanning an inbox.

## 4. Atomic Write Protocol

All message file writes must follow this protocol to prevent partial reads:

```
Step 1: Generate the final filename F.
Step 2: Write the complete JSON payload to F.tmp.
Step 3: Validate F.tmp against the mandatory schema.
Step 4: Rename F.tmp → F (atomic on POSIX filesystems).
Step 5: If rename fails, wait 100ms and retry once.
Step 6: If retry fails, log an error. Do not leave F.tmp in the inbox.
        Delete F.tmp and report the failure.
```

### Why Atomic Writes

Without atomic writes, a consumer scanning the inbox may read a partially
written file. The write-to-tmp-then-rename pattern guarantees that a file
either exists with complete content or does not exist at all. The POSIX
`rename(2)` system call is atomic within a single filesystem.

## 5. Directory Structure

```text
projects/<project>/message-queues/
├── <agent-a>/
│   ├── 20250725_143000123_agent-b.json       ← unread message from agent-b
│   ├── 20250725_143500456_agent-c.json       ← unread message from agent-c
│   └── archive/
│       └── 20250725_120000000_agent-b.json   ← read and archived
├── <agent-b>/
│   └── archive/
└── <agent-c>/
    └── archive/
```

## 6. Validation Rules

Before sending a message, the agent must validate:

1. All 5 mandatory fields are present.
2. `from` and `to` are non-empty strings.
3. `date` is a valid ISO 8601 timestamp with milliseconds and `Z` suffix.
4. `read` is exactly `false` (boolean, not string).
5. `message` is a non-empty string.
6. If `type` is present, it matches a value from `workflow-message-mapping.md`.
7. If `in_reply_to` is present, it is a valid filename matching the naming convention.
8. The filename matches the `YYYYMMDD_HHMMSSmmm_<sender>.json` pattern.
9. The `<sender>` component of the filename matches the `from` field value.

## 7. Example Messages

### Basic message

```json
{
  "from": "technical-lead",
  "to": "software-engineer",
  "date": "2025-07-25T14:30:00.123Z",
  "read": false,
  "message": "Please update the HLD for module X to reflect the new API endpoint added in CR-042."
}
```

Filename: `20250725_143000123_technical-lead.json`

### Governance message (SQA Audit — NCR)

```json
{
  "from": "sqa-auditor",
  "to": "technical-lead",
  "date": "2025-07-25T15:00:00.456Z",
  "read": false,
  "message": "Non-compliance detected: HLD peer review was not conducted before coding began for module Y. A Corrective Action Plan is required within 5 business days.",
  "type": "ncr",
  "ncr_id": "NCR-2025-003",
  "severity": "error"
}
```

Filename: `20250725_150000456_sqa-auditor.json`

### Reply message

```json
{
  "from": "technical-lead",
  "to": "sqa-auditor",
  "date": "2025-07-25T16:00:00.789Z",
  "read": false,
  "message": "Acknowledged. CAP: Will schedule HLD peer review for module Y by 2025-07-28. Root cause: review step was bypassed due to deadline pressure. Mitigation: adding review gate to CI pipeline.",
  "type": "corrective-action-plan",
  "ncr_id": "NCR-2025-003",
  "in_reply_to": "20250725_150000456_sqa-auditor.json"
}
```

Filename: `20250725_160000789_technical-lead.json`

### Read-marked message (after processing)

```json
{
  "from": "sqa-auditor",
  "to": "technical-lead",
  "date": "2025-07-25T15:00:00.456Z",
  "read": true,
  "read_date": "2025-07-25T16:00:00.789Z",
  "message": "Non-compliance detected: HLD peer review was not conducted before coding began for module Y. A Corrective Action Plan is required within 5 business days.",
  "type": "ncr",
  "ncr_id": "NCR-2025-003",
  "severity": "error"
}
```
