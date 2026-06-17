# Worked Example — STRIDE on a Banking Application

A complete end-to-end pass, to read when you want to *see* the method or to imitate
its output when producing your own threat table. The system is a banking app; the
same shape applies to any application.

## Step 1 — Scope and assets

**Under review:** a banking application (mobile/web client through to backend).

**Assets to protect:** user credentials and sessions; account balances and
transaction data; the funds-transfer function; customer PII; audit/log integrity;
administrative functions.

## Step 2 — DFD (textual)

External entities:
- **Customer** (mobile/web client)
- **Third-party integration** (e.g., Plaid)

Processes:
- **Authentication API**
- **Transaction API**

Data stores:
- **Accounts/transactions database**
- **Audit log store**

Data flows (crossings into the backend are trust boundaries, marked ‡):
- Customer → Authentication API: credentials ‡
- Customer → Transaction API: transfer request (amount, payee) ‡
- Transaction API → Accounts DB: read/write balances
- Transaction API → Audit log store: write transfer record
- Third-party integration → Transaction API: account data ‡

The three ‡ crossings (client→auth, client→transaction, third-party→transaction) are
where threat analysis concentrates.

## Step 3 — STRIDE walk (the threat table)

| ID | Element / flow | STRIDE | Threat | Mitigation | Priority |
|----|----------------|--------|--------|------------|----------|
| 1 | Customer → Auth API ‡ | **S** | Attacker steals credentials/session token and impersonates the user | Multi-factor authentication (MFA); strong session management | High |
| 2 | Customer → Transaction API ‡ | **T** | Attacker modifies the transfer amount in transit | Digitally sign transactions; validate and re-check on the server | High |
| 3 | Transaction API → Audit log | **R** | User claims they never made a transfer | Comprehensive logging; send notifications for transfers; signed/timestamped records | Medium |
| 4 | Customer ↔ backend flows ‡ | **I** | Attacker intercepts unencrypted traffic and steals data | HTTPS for all connections; encrypt data at rest | High |
| 5 | Authentication API | **D** | Attacker floods login with invalid requests | Rate limiting; CAPTCHAs | Medium |
| 6 | Transaction API → Accounts DB | **E** | User exploits SQL injection to gain admin rights | Sanitize all input; parameterized queries; least-privilege DB account | High |

Each row ties a STRIDE category to a specific element or trust-boundary crossing and
states what the attacker concretely does — concrete enough that a developer knows
what to build.

## Step 4 — Prioritize

STRIDE produced the six threats above; it does not rank them. Apply DREAD (Damage,
Reproducibility, Exploitability, Affected users, Discoverability) or a
likelihood×impact matrix to order them. Here, the credential-spoofing (1),
in-transit tampering (2), traffic interception (4), and SQLi privilege-escalation (6)
threats score as high business risk (broad affected users, high damage) and are
fixed first; the DoS (5) and repudiation (3) threats follow. The pattern:
**STRIDE to find, DREAD/risk-matrix to rank.**

## Step 5 — Mitigate and validate

Map each prioritized threat to the concrete control in its row, assign an owner and
deadline, implement, then validate that the control actually closes the threat
(e.g., confirm transfers are server-validated and signed for threat 2; confirm MFA
is enforced for threat 1). Treat the model as living: when the app adds a new data
flow (say, a new third-party payout integration), re-run the walk on the new
crossing and add rows.

## How the finished output should read

A good STRIDE deliverable is exactly this: a short asset list, a DFD (picture or
text) with trust boundaries marked, a threat table walking elements through the six
categories with concrete attacker actions and mitigations, a prioritization, and an
owner per high-priority row. Imitate this structure when running an exercise for the
user.
