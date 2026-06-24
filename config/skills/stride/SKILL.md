---
name: stride
description: >-
  Teaches STRIDE threat modeling (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) and guides users to enumerate, prioritize, and mitigate security threats in system designs.
---

# STRIDE Threat Modeling

STRIDE is a developer-focused framework, created at Microsoft by Loren Kohnfelder
and Praerit Garg in the late 1990s, for **systematically enumerating security
threats from a system's design** — before code is written, when fixes are cheapest.
It classifies every threat into one of six categories and pairs each with the
security property it violates, so a team works through a predictable checklist
rather than inventing threats from scratch.

Use this skill to run a threat-modeling exercise on a system the user describes, to
explain STRIDE, or to help the user build the habit. The core deliverable of a
STRIDE exercise is an **enumerated, prioritized list of threats with concrete
mitigations**, derived element-by-element from a model of the system.

## The mental model: four questions

A STRIDE exercise answers four questions in order. Keep them visible — they are the
spine of everything below:

1. **What are we working on?** — Understand and diagram the system: its components,
   data flows, trust boundaries, and assets.
2. **What can go wrong?** — Walk each element of the diagram through the six STRIDE
   categories and record every applicable threat.
3. **What are we going to do about it?** — For each threat, decide to mitigate,
   accept, transfer, or eliminate, and name a concrete countermeasure.
4. **Did we do a good enough job?** — Validate that mitigations address the threats,
   and revisit as the system evolves.

## The six categories

Each STRIDE letter is a threat type, the inverse of a desired security property.
Internalize the property column — it is what makes the category actionable. The
full table with detailed definitions, multiple examples, and countermeasure
catalogs per category is in `references/stride-categories.md`; read it when you need
depth on a specific category or are writing mitigations.

| Letter | Threat | Violates (property) | One-line example |
|---|---|---|---|
| **S** | Spoofing identity | Authentication | Stealing credentials/session tokens to impersonate a user; IP/DNS/ARP spoofing |
| **T** | Tampering with data | Integrity | Modifying a transaction amount in transit; injecting code into a build |
| **R** | Repudiation | Non-repudiation | A user denies making a transfer; an actor acts without traceable evidence |
| **I** | Information disclosure | Confidentiality | SQL injection dumps a customer DB; secrets exposed in errors or a public bucket |
| **D** | Denial of service | Availability | Flooding a login endpoint; a malformed request crashes a service |
| **E** | Elevation of privilege | Authorization | Exploiting a flaw to gain admin rights; abusing misconfigured permissions |

STRIDE maps directly onto the **CIA triad** plus authentication, authorization, and
non-repudiation. Spoofing↔authentication, Tampering↔integrity, Repudiation↔non-
repudiation, Information disclosure↔confidentiality, DoS↔availability, Elevation↔
authorization.

## The workflow

Run these steps when the user asks to threat model something. Steps 1–3 are the
heart; do not skip the diagram.

### Step 1 — Scope and inventory the assets

Name the application, service, or feature under review, and inventory what must be
protected: sensitive data, key functions, user interfaces, infrastructure,
identities, third-party integrations. A clear asset list is what later lets you
judge a threat's impact. If the user's description is thin, ask the one or two
questions that most affect the model (where does sensitive data live? who are the
external actors?) rather than guessing.

### Step 2 — Build a Data Flow Diagram (DFD) and mark trust boundaries

STRIDE works best when you can see how data moves. A DFD is built from exactly five
element types — learn these once and you can read or draw any DFD:

- **External entities** (rectangles): actors outside your system — users, third-party
  services, IoT devices.
- **Processes** (circles/ovals): components that transform data — web servers,
  microservices, functions.
- **Data stores** (parallel lines): where data rests — databases, file systems,
  caches, queues.
- **Data flows** (arrows): movement of data between components, labeled with what
  moves.
- **Trust boundaries** (dashed lines): any place where data crosses between
  different levels of trust. **Every trust-boundary crossing is a prime threat
  analysis point** — it is where validation is most needed and where attacks
  concentrate.

If you cannot render an image, describe the DFD textually as a list of elements and
the flows between them; that is sufficient to drive Step 3. For diagram-construction
detail and worked DFD reasoning, see `references/dfd-and-trust-boundaries.md`.

### Step 3 — Walk each element through STRIDE

This is the engine of the method. Two standard approaches (see
`references/dfd-and-trust-boundaries.md` for when to use which):

- **STRIDE-per-element**: for each process, data store, data flow, and external
  entity, ask the six questions — can this be **s**poofed, **t**ampered with,
  **r**epudiated, **e**xposed (info disclosure), **d**enied (DoS), or **e**scalated?
  Record every applicable threat. This is the right default and the most thorough.
- **STRIDE-per-interaction**: analyze threats on the interaction between a pair of
  components rather than each component alone. Lighter weight for large systems.

Not every category applies to every element — that is expected. The discipline is
asking all six of every element so nothing is missed, then recording only what
genuinely applies, ideally tied to the specific trust boundary or flow it threatens.

Produce a **threat table** as you go (this is the required output format):

```
| ID | Element / flow | STRIDE | Threat (what an attacker does) | Mitigation | Priority |
```

### Step 4 — Assess and prioritize

STRIDE *enumerates* threats; it does not score them. To prioritize, layer a risk
method on top — most commonly **DREAD** (Damage, Reproducibility, Exploitability,
Affected users, Discoverability) or a simple likelihood×impact matrix. The standard
pairing: **use STRIDE first to find threats, then DREAD/risk-matrix to rank them**
so you fix the highest-business-risk items first. Threat modeling feeds risk
assessment; they are complementary, not the same activity.

### Step 5 — Mitigate, then validate and iterate

For each prioritized threat, choose mitigate / accept / transfer / eliminate and
name a concrete control (see the countermeasure catalogs in
`references/stride-categories.md`). Then validate that the controls actually address
the threats, and treat the threat model as a **living document**: revisit on every
major architectural change, when adding data flows or trust boundaries, when
integrating third parties, after a security incident, and on a regular cadence
(e.g., quarterly for critical systems). In DevSecOps, encode the model (YAML/JSON)
and validate it in CI/CD.

## Worked example

For a complete end-to-end pass on a banking application — DFD, the six threats with
mitigations, prioritization, and how the output reads — see
`references/worked-example-banking.md`. Point to it when the user wants to *see* a
full exercise rather than read the method, or use it as the template to imitate when
producing your own threat table.

## Practical guidance and pitfalls

- **Lead with the diagram, not the checklist.** Teams that skip the DFD produce
  vague threat lists. The diagram is what makes attack surface visible.
- **Timebox** when running a live session: e.g. 30 min DFD, 30 min STRIDE walk, 15
  min prioritization. Aim for a good-enough model, not a perfect one.
- **Start small and specific.** Model the feature being built, not the whole system,
  especially to win developer buy-in — catching one real bug before it ships earns
  more trust than an exhaustive survey.
- **Write threats and mitigations in plain language** developers can act on, with a
  clear owner and deadline. A threat nobody understands does not get fixed.
- **Known limitations to be honest about:** STRIDE relies on manual effort and
  expertise, scoring is subjective without a layered method, and models go stale
  fast without a refresh cadence. STRIDE tells you *what could* go wrong by design;
  it does not, by itself, tell you which real-world attack techniques are active
  (pair with MITRE ATT&CK) or how a specific attacker would chain steps.

## When the user is preparing for an interview

If the request is interview prep, focus on crisp definitions of the six categories
and their violated properties, the difference between threat modeling and risk
assessment, what a trust boundary is, and the STRIDE→DREAD prioritization pairing.
`references/interview-prep.md` has the high-frequency questions with model answers.

## How to respond

When asked to threat model a described system, do not just explain STRIDE — *apply*
it: inventory assets, lay out the DFD elements and trust boundaries in text, produce
the filled threat table walking elements through the six categories, then prioritize
and give concrete mitigations. When asked to explain or teach STRIDE, use the
four-questions spine and the six-category table, and offer to run a real exercise on
something the user is building.
