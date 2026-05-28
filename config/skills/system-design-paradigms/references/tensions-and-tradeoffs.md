# Tensions and Tradeoffs Between Paradigms

Most design problems aren't about applying one principle; they're about choosing between several that point in different directions. The skill is recognizing the tension you're in and reasoning through it deliberately, instead of being captured by whichever principle happens to be top-of-mind.

This reference walks through the most common tensions, what each side is protecting, and how to navigate.

---

## DRY vs. YAGNI

**The tension:** DRY says deduplicate; YAGNI says don't build abstractions you don't need yet. The instant you have two similar pieces of code, you can either extract a shared abstraction (DRY) or leave them alone (YAGNI).

**What each is protecting:** DRY guards against bugs of inconsistency — the same business rule going stale in one of three copies. YAGNI guards against speculative generality — abstractions designed for a future that never arrives, which then make the present harder to change.

**How to resolve:** the "Rule of Three" is the usual heuristic. The first occurrence is a fact. The second is a coincidence. The third is a pattern, and now you know enough about the actual shape of the duplication to abstract well. Abstracting from two examples almost always means inventing the wrong shape — and a wrong abstraction is far more expensive than the duplication it replaced.

A related test: **is this the same knowledge, or just the same syntax?** Two functions that *look* identical may represent unrelated concepts that happen to share a structure today. Merging them couples things that should be allowed to diverge.

---

## DRY vs. Loose Coupling (especially across services)

**The tension:** sharing code is the most natural way to DRY. Sharing code between services *couples* them — they now deploy together, version together, and break together.

**What each is protecting:** DRY protects against bug duplication. Loose coupling protects against deploy-time and runtime entanglement.

**How to resolve:** DRY within a service; tolerate duplication across services. A shared library at the service boundary turns "independent services" into "a distributed monolith" — you've split the runtime without splitting the deployment. The cost of a little duplicated logic across services is almost always less than the cost of recombining their release cycles.

The exception: code that genuinely *must* be identical (a wire-protocol schema, a cryptographic algorithm) is fine to share. The test is whether divergence between services is harmful or harmless.

---

## KISS vs. Design for Failure

**The tension:** the simplest possible system has no retries, no circuit breakers, no fallbacks. Designing for failure adds machinery that the happy path doesn't need.

**What each is protecting:** KISS protects against the tax of complexity on everyone reading the code later. Design for Failure protects against outages when (not if) components fail.

**How to resolve:** add failure handling for the failure modes that are *real* and *likely*, not the ones that are hypothetical. A retry on a network call to a remote service: clearly worth it. A circuit breaker on an in-process function call: clearly not. The middle is where judgment lives — and it depends on the blast radius of failure.

A useful frame: KISS applies to *internal* complexity (code you can read). Design for Failure applies to *external* complexity (the world you can't control). They mostly don't conflict; they're protecting against different categories of risk.

---

## Convention over Configuration vs. Principle of Least Astonishment

**The tension:** conventions are great when they match expectations and terrible when they don't. A convention the user doesn't know about is, by definition, astonishing.

**What each is protecting:** Convention over Configuration protects against decision fatigue. PoLA protects against silent misuse from mismatched mental models.

**How to resolve:** conventions only earn their keep if they match the audience's *existing* mental model. If you have to teach the convention before it becomes useful, it isn't really a convention — it's a configuration with a default and a steeper learning curve. The fix is either to pick a convention people already expect, or to make the surprising behavior obvious at the point of use.

---

## Composition over Inheritance vs. Simplicity

**The tension:** heavy composition can produce a constellation of tiny pieces wired together at runtime — flexible, but harder to follow than a straightforward inheritance hierarchy.

**What each is protecting:** Composition over Inheritance protects against the rigidity of deep class trees. Simplicity protects against navigation overhead.

**How to resolve:** compose at meaningful seams — places where behavior actually varies across instances. Composing at every method just shuffles the complexity into the wiring layer. If there's only one implementation of a "strategy," it shouldn't be a strategy yet.

---

## SOLID (especially SRP) vs. Pragmatism

**The tension:** taken to extremes, SRP produces a million one-method classes. Each class is simple in isolation; the system as a whole is incomprehensible.

**What SRP is protecting:** classes that change for unrelated reasons and become merge-conflict nests.

**How to resolve:** the unit of responsibility is a *reason to change*, not a verb. A class with eight methods that all serve the same stakeholder is fine; a class with two methods that serve two different stakeholders is not. Count change reasons, not methods.

---

## Consistency vs. Availability (CAP)

**The tension:** CAP forces you to pick one during a network partition. Strong consistency means rejecting writes (or reads) when replicas can't talk; high availability means accepting writes and reconciling later.

**What each is protecting:** Consistency protects against contradictory views of the data — two clients seeing different bank balances, for example. Availability protects against being down whenever the network hiccups.

**How to resolve:** pick **per use case**, not per system. A real system usually needs both — strong consistency on payments and inventory, eventual consistency on product listings and recommendations. Picking globally throws away the win on whichever side you didn't pick.

The practical implication is architectural: data that needs strong consistency goes into one kind of store (RDBMS, Spanner, a Raft-backed system); data that needs availability goes into another (Dynamo-style stores, queues, caches). Mixing both in one store is hard and often forces compromise on both sides.

---

## Statelessness vs. Performance

**The tension:** stateless services often need an extra round trip to a state store (cache, database, session store) on every request. A stateful service that holds the data locally can be much faster.

**What each is protecting:** Statelessness protects horizontal scalability and failure recovery. Performance protects user experience and operational cost.

**How to resolve:** push *authoritative* state to a backing service; cache *derived* state at the edges. The service stays stateless in the sense that any instance can handle any request (if the cache is missing, it can be rebuilt from the authoritative source) — but it's not paying the full round trip on every call. Sticky sessions are the anti-pattern this is meant to avoid.

---

## End-to-End Principle vs. Convenience of Centralization

**The tension:** putting logic at the edges keeps the core dumb and fast. Putting logic in the middle (a smart load balancer, a stored procedure, a service mesh policy) is often *convenient* — one place to change, one place to monitor.

**What each is protecting:** the end-to-end principle protects against bottleneck-by-design and protocols that don't scale. Centralization protects against fragmentation and policy drift.

**How to resolve:** centralize *policy*, distribute *mechanism*. A service mesh enforcing mTLS everywhere: good — it's a uniform mechanism. A service mesh containing domain logic for one specific feature: bad — it's a feature in the wrong layer. The test is whether the central thing is enforcing a *uniform* concern or a *specific* one.

---

## Premature Optimization vs. Architectural Performance Choices

**The tension:** Knuth's quote is famous, but the *full* quote ends with "yet we should not pass up our opportunities in that critical 3%." Some performance choices belong upfront; others belong after profiling.

**How to resolve:**
- **Architectural choices upfront:** data model, where you put the bottleneck, sync vs. async, the consistency tier of each piece of data, whether to introduce a cache layer at all. These are expensive to change later because everything depends on them.
- **Micro-optimizations after profiling:** loop unrolling, allocation reduction, string-builder usage, etc. These are cheap to change and almost never matter outside the hot path. Measuring first ensures you optimize the right code.

The mistake is to apply Knuth's quote to all performance work — including the architectural choices that are going to determine whether the system can perform at all. Those aren't premature; they're foundational.

---

## A useful meta-frame

When two principles conflict, ask:

1. **What is each principle protecting against?** Both are real failure modes. The question is which failure mode is more likely or more costly in *your* situation.
2. **Can you defer the choice?** Sometimes the right answer is to pick the simpler side now and add the other later if it actually becomes necessary. (This is also why YAGNI tends to win the abstraction debate — abstractions are easy to add and hard to remove.)
3. **Is the conflict at the right level?** A lot of apparent tensions dissolve when you separate concerns — DRY within a service and duplication across, consistency for payments and availability for catalog, etc.

The goal isn't to maximize adherence to all principles simultaneously. It's to understand the tradeoffs well enough to make the choice that fits the system you're actually building.
