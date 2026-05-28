---
name: system-design-paradigms
description: A reference and applied guide to major software system design paradigms — KISS, DRY, YAGNI, Separation of Concerns, SOLID, Law of Demeter, High Cohesion / Low Coupling, Encapsulation, Composition over Inheritance, Convention over Configuration, Fail Fast, Idempotency, Statelessness, CAP theorem, Eventual Consistency, Design for Failure, Horizontal Scaling, Cacheability, Premature Optimization, End-to-End Principle, and the Twelve-Factor App. Use aggressively whenever the user is designing, reviewing, critiquing, or studying a software system — microservices vs. monolith debates, API design, database choices, scaling and reliability questions, architecture reviews, refactoring decisions, distributed systems tradeoffs, system design interview prep, or any conversation about architecture tradeoffs. Trigger even when the user doesn't name a principle explicitly — if they're weighing a design choice, the relevant paradigms are part of the answer.
document_id: SKILL-SYSDESIGN-001
version: "1.0"
baseline_id: BL-SYSDESIGN-001
---

# System Design Paradigms

## What this skill is for

These paradigms are the accumulated wisdom of decades of building software. They're not laws — they're heuristics. Each one captures a recurring failure mode and a default that works most of the time. The skill of system design is knowing **which principles apply, which are in tension, and which to bend for the situation in front of you**.

Use this skill to:

- **Name the principle** when a design choice maps to one. Naming sharpens the discussion ("this violates SRP" is more actionable than "this feels wrong").
- **Explain the why**, not just the rule. Every principle exists because of a specific past pain; understanding the pain is what lets someone apply it correctly.
- **Surface tensions** between principles. DRY pulls toward abstraction; YAGNI pulls away from it. CAP forces a choice. Good design is navigating these, not pretending they don't exist.
- **Resist dogma.** Any principle, taken too far, becomes its own anti-pattern. Over-applied DRY produces god abstractions. Over-applied SRP produces a fog of one-method classes.

When the user is doing system design work, weave these in naturally — don't recite a list, point to the principle that fits the moment and explain it. If they're studying, you can also drill, quiz, or compare on request.

---

## Foundations of simplicity

These are the principles that resist complexity. They're listed first because complexity is the default outcome of any sufficiently long-lived system, and these are the counterweights.

### KISS — Keep It Simple, Stupid

Favor straightforward solutions. The simplest design that meets the actual requirements wins. Complexity must be **earned**, not assumed.

Why it matters: every bit of complexity is a recurring tax — on reading, debugging, onboarding, and changing the system later. Clever code optimizes for the moment of writing; simple code optimizes for the years afterward.

Common failure: confusing "fewer lines" with "simpler." A dense one-liner can be much more complex than a verbose, obvious version. Simplicity is about how easy the design is to *understand*, not how compact it is on the page.

### DRY — Don't Repeat Yourself

Every piece of knowledge should have a single, authoritative representation in the system. If a business rule lives in three places, two of them will eventually go stale.

Why it matters: duplicated knowledge means duplicated bugs and inconsistent behavior. The cost shows up at change time, not at write time.

Common failure: DRYing up code that *looks* the same but represents *different* concepts. Two functions that happen to share lines today may diverge tomorrow. Premature deduplication couples unrelated things and makes both harder to change. The right test is: "is this the same knowledge, or just the same syntax?"

### YAGNI — You Aren't Gonna Need It

Don't build for hypothetical future needs. Build for the requirements you actually have.

Why it matters: speculative generality is one of the most expensive forms of waste. The hypothetical use case rarely materializes, but the abstraction stays — making everything around it harder to read and change.

Common failure: confusing YAGNI with "don't think ahead." You should think ahead. You just shouldn't *build* ahead. Leaving a clean seam is fine; building the feature behind the seam is not.

### Principle of Least Astonishment (PoLA)

A system should behave the way a reasonable user or developer expects. Surprising behavior is a bug, even if it's "technically correct."

Why it matters: people build mental models from a few interactions and then trust them. Violating those models causes silent misuse — the worst kind, because it doesn't look like an error.

Common failure: cute APIs. A `delete()` method that returns the deleted item is fine; one that *also* writes to a log file is astonishing.

### Convention over Configuration

Provide sensible defaults so users only configure the exceptions. Make the common path the default path.

Why it matters: every configuration option is a question the user is forced to answer. Most of those questions have a right answer 95% of the time — bake it in.

Common failure: hiding configuration so well that the 5% case becomes impossible. Conventions should be defaults, not prisons.

### Worse Is Better

A simple, incomplete implementation that ships often beats an elegant, complete one that doesn't. Worse-is-better systems spread, get patched in the field, and eventually become the standard.

Why it matters: this is the principle behind C, Unix, the Web, and most successful infrastructure. Elegance loses to availability. A working 70% solution today is worth more than a beautiful 100% solution in two years.

Common failure: using this as cover for shipping bad work. The principle is about *prioritizing simplicity of implementation over completeness*, not about lowering quality bars on what you do ship.

---

## Modularity and structure

These principles govern how a system is decomposed — how the boundaries between parts are drawn.

### Separation of Concerns (SoC)

Different aspects of the system (UI, domain rules, persistence, transport) belong in different modules. Each module addresses one concern and doesn't know about the others.

Why it matters: when concerns are tangled, every change ripples. Separating them means changing the database doesn't break the UI, and rewriting the UI doesn't touch business rules.

Common failure: drawing the wrong seams. MVC-style layers are *one* separation; sometimes the right separation is by feature (vertical slice) rather than by layer. The principle is about clean boundaries, not a specific layering scheme.

### Single Responsibility Principle (SRP)

A module or class should have one reason to change. If two unrelated stakeholders can both force it to change, it has two responsibilities.

Why it matters: SRP is the class-level version of SoC. Multi-purpose classes become merge conflict magnets and bug nests because every change has unrelated knock-on effects.

Common failure: interpreting "one responsibility" as "one method." That produces a wasteland of trivial classes. The unit of responsibility is a *reason to change*, not a verb.

### High Cohesion, Low Coupling

Things that change together should live together (cohesion). Things that don't shouldn't know about each other (coupling).

Why it matters: this is the operational test of a good decomposition. Low cohesion (scattered related code) and high coupling (everything depends on everything) are the two failure modes that make codebases unworkable.

Common failure: optimizing for one and ignoring the other. Splitting a coherent module to "reduce coupling" often just spreads the coupling around.

### Encapsulation / Information Hiding

Hide internal state and implementation details. Expose only a stable interface. The caller shouldn't be able to tell — or care — how a thing works inside.

Why it matters: encapsulation is what makes refactoring possible. If callers depend on internals, you can't change internals without breaking callers.

Common failure: leaky abstractions — interfaces that expose enough of the implementation that callers end up coupled to it anyway (an ORM that requires you to think about SQL to use efficiently, for example).

### Law of Demeter (Principle of Least Knowledge)

A unit should only talk to its immediate collaborators, not reach through them. `a.b.c.do_thing()` is a code smell — `a` is now coupled to the internals of `b`.

Why it matters: chained access creates fragile, brittle coupling across multiple layers. Any change to `b`'s shape can break `a`.

Common failure: applying it religiously to data structures. The law is about *behavior*, not data. Walking a tree node-by-node isn't a violation.

### Composition over Inheritance

Build behavior by combining small objects rather than by extending deep class hierarchies. Prefer "has-a" to "is-a" when both are plausible.

Why it matters: inheritance hierarchies are rigid. They couple subclasses to base-class internals and lock in a single axis of variation. Composition lets you mix behaviors more flexibly and changes far more cheaply.

Common failure: using inheritance because the language makes it the obvious tool. The right question is "do these things actually share an identity, or just some behavior?"

### SOLID

A bundle of five OO principles: **S**ingle Responsibility, **O**pen/Closed, **L**iskov Substitution, **I**nterface Segregation, **D**ependency Inversion. Together they describe what well-factored OO code looks like.

For depth on each principle with examples, see `references/solid.md`.

---

## Robustness and operability

How systems behave under stress, failure, and load.

### Fail Fast

Surface errors as early and as loudly as possible. Don't paper over invalid state — crash on it.

Why it matters: silent failures compound. A bad value caught at the boundary is a small bug; the same value smuggled three layers deep is a debugging nightmare with no stack trace pointing at the cause.

Common failure: confusing fail-fast with fail-rude. Failing fast means detecting *internal* invariant violations early; it doesn't mean dumping stack traces at end users.

### Design for Failure

Assume every component will fail — network, disk, dependent service, your own process. Build retries, timeouts, circuit breakers, and graceful degradation in from day one.

Why it matters: in a system of N components each with 99.9% uptime, total uptime drops fast as N grows. The only systems that stay up are the ones that expect failure.

Common failure: treating failure handling as cleanup work for later. The retry/timeout/fallback decisions shape the system's architecture; bolting them on after the fact rarely works.

### Idempotency

An operation is idempotent if running it twice has the same effect as running it once. Critical for any API that might be retried — which, in distributed systems, is all of them.

Why it matters: networks lose responses, not just requests. Without idempotency, the client can't safely retry — it doesn't know whether the first call succeeded.

Common failure: making *reads* idempotent (which is easy) and forgetting *writes* (which is the hard part). Use idempotency keys, dedupe on the server, or design operations to be naturally idempotent (PUT vs. POST).

---

## Distributed systems

When the system spans multiple machines, a whole new set of constraints kicks in.

### CAP Theorem

In the presence of a network partition (P), a distributed system must choose between Consistency (C) and Availability (A). You don't get all three.

Why it matters: this isn't a tradeoff you can engineer your way out of — it's a property of the universe. Every distributed data store has made this choice; understanding which one tells you what your system can and can't promise.

Common failure: treating CAP as "pick two." Partitions happen whether you like it or not; the real choice is C-or-A *during a partition*. Outside a partition, you can usually have both.

### Eventual Consistency

Replicas may temporarily disagree, but if writes stop, they will converge. The tradeoff: weaker guarantees for higher availability and scale.

Why it matters: most large-scale systems (DNS, S3, most NoSQL) are eventually consistent. Accepting this lets you scale; rejecting it forces you into expensive coordination.

Common failure: assuming "eventually" is fast. Convergence windows can be milliseconds or minutes depending on the system. If your UX depends on "read your own writes," you need stronger guarantees on that path.

### Statelessness

Keep services stateless where possible. Move session/conversation state to a shared store or push it back to the client.

Why it matters: stateless services scale horizontally trivially and recover from failure trivially — any replica can handle any request. Stateful services need sticky sessions, careful failover, and complicated rebalancing.

Common failure: declaring a service "stateless" while it caches things in process memory. Cache is state. The test is: can you kill any instance and have requests still work?

### Loose Coupling via Messaging

Decouple services by putting an async queue or event bus between them. The producer doesn't know who consumes; the consumer doesn't know who produced.

Why it matters: async messaging absorbs spikes, isolates failures, and lets services evolve independently. The producer can keep producing when the consumer is down.

Common failure: treating async as a magic fix. Async introduces its own complexity — ordering, duplication, eventual consistency, harder debugging. Use it where the decoupling earns the cost.

### End-to-End Principle

Put functionality at the edges of the system; keep the core dumb and fast. The endpoints know what they need; the network just moves bytes.

Why it matters: this is the principle behind IP, the Web, and most successful protocols. Trying to put smarts in the middle creates fragility and bottlenecks; smarts at the edges scale.

Common failure: putting domain logic in the message bus, the database, or the load balancer because "it's convenient." Convenient now, brittle later.

---

## Performance and scale

### Horizontal Scaling over Vertical

Add more machines rather than bigger machines. Vertical scaling hits hardware ceilings; horizontal scaling has runway as long as your architecture allows.

Why it matters: horizontal scaling forces you to design for statelessness, partitioning, and failure — properties that pay off in many other ways. Vertical scaling is a short-term escape that delays the real work.

Common failure: assuming horizontal is always better. For some workloads (single huge database, in-memory analytics), a bigger box is genuinely the right answer. The principle is a default, not a law.

### Cacheability

Identify read-heavy paths and cache aggressively. Make cache invalidation explicit — it is famously one of the two hard problems in computer science.

Why it matters: a cache hit is roughly free; the underlying query may be expensive. Order-of-magnitude wins are routine here when applied to hot paths.

Common failure: caching without an invalidation story. The cache that returns stale data three days after a change has caused more outages than the database it was protecting.

### Premature Optimization is the Root of All Evil

Don't optimize before you measure. Most code doesn't matter for performance; some code matters enormously. Profile, then optimize the hot paths.

Why it matters: optimization usually trades clarity for speed. If the code you obfuscated wasn't the bottleneck, you paid the cost and got nothing.

Common failure: quoting this as an excuse for never thinking about performance. Knuth's full quote includes "yet we should not pass up our opportunities in that critical 3%." Architectural performance choices (data model, where to put the bottleneck, sync vs. async) belong upfront. Micro-optimizations belong after profiling.

---

## Operational discipline

### Twelve-Factor App

A checklist for building cloud-native services: explicit dependencies, config in environment, stateless processes, port binding, disposability, dev/prod parity, and so on.

Why it matters: most of these factors are about removing implicit assumptions that break when the app moves between environments. A twelve-factor app deploys to a new environment without surprises.

For the full list with notes on each factor, see `references/twelve-factor.md`.

---

## Navigating tensions between principles

Real design problems sit at the intersection of multiple principles, which often pull in opposite directions. The signs of skill are recognizing which tension you're in and choosing deliberately.

Quick reference of common tensions:

- **DRY vs. YAGNI** — Abstracting eagerly to avoid duplication often produces speculative generality. The resolution: tolerate duplication until the third occurrence reveals the real shape.
- **DRY vs. Loose Coupling** — Sharing code across services *couples* them. The resolution: prefer duplication across service boundaries; DRY within a service, not across.
- **Convention over Configuration vs. PoLA** — A surprising convention is worse than explicit configuration. The resolution: conventions must match the audience's existing mental model.
- **KISS vs. Design for Failure** — Failure handling adds complexity. The resolution: complexity for *real* failure modes earns its place; for hypothetical ones, it doesn't (YAGNI).
- **Consistency vs. Availability (CAP)** — Forced choice during a partition. The resolution: pick per use case, not per system. Payments need C; product listings can take A.
- **Statelessness vs. Performance** — Stateless services often mean an extra round trip to a state store. The resolution: cache hot state at the edges, persist authoritative state centrally.
- **Composition vs. Simplicity** — Heavy composition can produce a maze of tiny pieces. The resolution: compose at meaningful boundaries, not at every method.

For a deeper treatment of these tensions with examples, see `references/tensions-and-tradeoffs.md`.

---

## How to apply this skill in conversation

When the user is doing system design work:

1. **Don't recite.** Find the one or two principles that actually fit their situation and apply them. A reply that name-drops eight principles is worse than one that uses two well.
2. **Show the tension.** If their choice has a real tradeoff, surface it. Good design discussions are about which tradeoff to pick, not about pretending one side dominates.
3. **Explain the why.** A principle without its motivation is just a rule, and rules without reasons get misapplied. Always include the failure mode the principle is guarding against.
4. **Resist dogma.** If applying a principle in the user's specific case would make things worse, say so. The principles are heuristics; the user's situation is real.
5. **Use the references.** For SOLID, Twelve-Factor, and deep tradeoff analysis, pull the relevant reference file rather than reproducing it inline.

If the user is studying — quizzing themselves, preparing for interviews, building intuition — engage that mode directly: explain a concept on demand, contrast two principles, walk through a worked example, or pose a question back to them.

*This document is a Configuration Item (CI) under baseline BL-SYSDESIGN-001.
Changes require Change Control Board approval per `cmmi-glue` Workflow 2.*
