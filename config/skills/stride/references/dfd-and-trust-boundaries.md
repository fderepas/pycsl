# Data Flow Diagrams and Trust Boundaries

A STRIDE analysis is driven by a Data Flow Diagram (DFD) of the system. The DFD is
not decoration — it is what makes attack surface visible and tells you *where* to
apply the six categories. Skipping it turns threat modeling into guesswork.

## Why the DFD comes first

A DFD gives the whole team — developers, architects, security engineers, product
managers — a shared map of how data moves through the system. It exposes trust
boundaries, entry points, data stores, and the exact paths an attacker could
exploit. DFDs are the most widely used diagramming technique in threat modeling and
are referenced as a core component of secure design by Microsoft, NIST (SP 800-154),
ISO 27001, and the EU Cyber Resilience Act. They underpin STRIDE, PASTA, LINDDUN,
VAST, and OCTAVE.

## The five DFD elements

Every DFD, regardless of tool or methodology, is built from exactly five element
types. Learn these once and you can read or draw any DFD:

1. **External entity** — a solid rectangle. Any person, system, or organization
   outside the scope of your system that interacts with it (users, third-party
   services, IoT devices).
2. **Process** — a circle or oval. A component that transforms data: a web server,
   microservice, or function.
3. **Data store** — parallel lines. Where data rests: databases, file systems,
   caches, message queues.
4. **Data flow** — an arrow. The movement of data between components, labeled with
   *what* data moves.
5. **Trust boundary** — a dashed line. Any place where data crosses between
   different levels of trust.

## Trust boundaries are the high-value targets

A **trust boundary** is any place in the system where data flows that changes its
level of trust; these are often also attack boundaries. Example: a web server that
receives purchase orders validates the order data, raising the trust level of that
data once inside. You generally need fewer restrictions around already-high-trust
data and more scrutiny exactly where data crosses inward.

**Every trust-boundary crossing is a threat analysis point.** When walking the DFD,
give crossings disproportionate attention — they are where authentication,
validation, and authorization are most needed and where attacks concentrate.

## Levels of abstraction

DFDs can be drawn at multiple levels:
- **Level-0 (context diagram):** the whole system as one process with its external
  entities and the major flows — a system overview.
- **Level-1 and deeper:** decompose the system into its components and show
  component-level flows and internal trust boundaries.

Start at Level-0 to frame scope, then decompose the areas that carry sensitive data
or cross trust boundaries. Hierarchical decomposition lets you go only as deep as
the risk warrants.

## STRIDE-per-element vs STRIDE-per-interaction

Two standard ways to apply the six categories against the DFD:

- **STRIDE-per-element.** Analyze each element (process, data store, data flow,
  external entity) on its own, asking all six questions of it. Most thorough; the
  right default; best when you can afford a careful pass. Not every category applies
  to every element type — but ask all six anyway so gaps are deliberate, not
  accidental.
- **STRIDE-per-interaction.** Analyze the threats arising from the interaction
  between a *pair* of components rather than each component in isolation. Lighter
  weight and more scalable for large systems, at some risk of missing element-local
  issues.

A useful heuristic for which categories tend to attach to which element types:
external entities attract Spoofing and Repudiation; processes can attract all six;
data stores attract Tampering, Information disclosure, Repudiation (of log stores),
and DoS; data flows attract Tampering, Information disclosure, and DoS. Treat this as
a prompt, not a constraint — still ask all six.

## Turning the DFD into the threat walk

For each element (or interaction), produce rows in the threat table:

```
| ID | Element / flow | STRIDE | Threat (what an attacker does) | Mitigation | Priority |
```

Anchor each threat to the specific element or trust-boundary crossing it applies to.
That anchoring is what makes the resulting list concrete enough for a developer to
fix, and what lets you check coverage (did every crossing get examined against all
six?).

## When you cannot draw

If image rendering is unavailable, express the DFD as text: list the external
entities, processes, and data stores; list the data flows as `source → dest: what
data`; and mark which flows cross a trust boundary. This textual DFD drives the
STRIDE walk just as well as a picture.
