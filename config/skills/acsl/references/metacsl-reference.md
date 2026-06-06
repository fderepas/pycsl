# MetAcsl Reference (High-Level ACSL Requirements)

Exhaustive reference for **MetAcsl**, the Frama-C plug-in for specifying and
verifying *pervasive*, high-level properties that would be intractable to write
as ordinary ACSL contracts. Developed primarily by Virgile Robles (PhD), with
Nikolai Kosmatov, Virgile Prevosto, Louis Rilling, and Pascale Le Gall.

## Table of contents
1. What problem MetAcsl solves
2. The HILARE model: target, context, property
3. Targets
4. Contexts and meta-variables
5. Concrete syntax (and its evolution across releases)
6. Verification by transformation (semantics)
7. Why `\writing` beats `assigns`
8. CLI, backends, installation
9. The canonical confidentiality case study
10. When to reach for MetAcsl

---

## 1. What problem MetAcsl solves

Modular deductive verification proves each function against its contract. But a
high-level (often security) property — isolation, integrity, confidentiality —
typically **spans the whole module**. Encoded as ordinary contracts, it gets
*split across many clauses in many functions with no explicit link*. Even if
each clause is proved, a reviewer or certifier cannot easily see that the global
property actually holds, and a later code edit can silently break it.

MetAcsl lets you state the property **once**, as a *HILARE* (HIgh-Level Acsl
REquirement), and have the plug-in generate all the corresponding low-level ACSL
annotations automatically — one per matching program point. A single HILARE can
expand into a very large number of ACSL clauses. The trade-off: that expansion
can be costly (many goals) on large code or many properties.

---

## 2. The HILARE model: target, context, property

A HILARE (a "meta-property") is **not** attached to one function. It is defined
at global scope from three ingredients:

1. **Target** — the set of functions where the requirement must hold.
2. **Context** — *which program points* within those functions are checked
   (every point? each write? each read? entry/exit only?). The context may
   introduce **meta-variables**.
3. **Property** — an ordinary ACSL predicate, possibly using the context's
   meta-variables, that must hold at those points.

Formally a meta-property is a triple `(c, F, P)`: "for every function `f` in `F`,
property `P` holds in context `c`". `P` must only mention global objects plus the
meta-variables provided by `c`.

---

## 3. Targets

The target set is `F = F+ \ F-` (included minus excluded).

- Default: `F+` = all functions, `F-` = empty (the HILARE applies everywhere).
- Excluding is the common pattern — "every function *except* the one privileged
  to do X". This is far less error-prone than enumerating every function that
  *may* do X.
- In the documented (TACAS 2019) syntax, targeting uses the ACSL `\forall
  function f;` binder, optionally combined with `\subset(f, {g1, g2, ...})` (and
  its negation) to include/exclude specific functions.

---

## 4. Contexts and meta-variables

Four contexts cover the motivating case studies; the two most important are
`\writing` and `\reading`.

- **`weak_invariant`** — `P` must hold at the **beginning and end** of each target
  function (a boundary invariant).
- **`strong_invariant`** — `P` must hold at **every program point** (every
  sequence point) of each target function.
- **`\writing`** — `P` must hold at **every memory write** in the target
  functions. Provides the meta-variable **`\written`**, the location being
  written to. This is the lever for **integrity** properties ("nobody but X may
  modify this").
- **`\reading`** — `P` must hold at **every memory read**. Provides the
  meta-variable **`\read`**, the location being read. This is the lever for
  **confidentiality** properties ("nobody without clearance may read this").

Memory-access contexts apply to direct accesses (stack and heap); function calls
are handled by checking the property inside the callee under its own target
membership, which is what makes the restriction *non-transitive* (see §7).

---

## 5. Concrete syntax (and its evolution)

**Documented baseline (TACAS 2019 / TAP 2019).** A meta-property `(c, F, P)` is
written:

```c
/*@ meta <NAME>:
      \forall function f; <target/context expression>(f),
      <ACSL property over globals and meta-variables>;
*/
```

Worked clauses from the original confidentiality study:

```c
/*@ meta M_1: \forall function f; \strong_invariant(f),
      \forall integer page; 0 <= page < PAGE_NB ==>
        metadata[page].status == FREE || metadata[page].status == ALLOCATED;

    meta M_2: \forall function f;                       // only page_encrypt may
      \subset(f, {page_encrypt}) ==> \writing(f),       // change an allocated
      \forall integer page; 0 <= page < PAGE_NB &&      // page's level
        metadata[page].status == ALLOCATED ==>
        \separated(\written, &metadata[page].level);

    meta M_3: \forall function f; \reading(f),          // no read of a confidential
      \forall integer page; 0 <= page < PAGE_NB &&      // page above clearance
        metadata[page].status == ALLOCATED &&
        metadata[page].level == CONFIDENTIAL && user_level == PUBLIC ==>
        \separated(\read, metadata[page].data + (0 .. PAGE_LENGTH - 1));
*/
```

**Evolution.** Across releases (companion MetAcsl release per Frama-C version
since **22.0 Titanium**) the concrete spelling of the three ingredients
(name / target / context / property) has been refined under the HILARE framing.
The semantics — target, context (`\writing`/`\reading`/invariants), and
meta-variables (`\written`/`\read`) — are stable, but **the exact keyword form
is version-specific**. When producing syntax for a user, match it to their
Frama-C/MetAcsl version and confirm against the manual bundled in the MetAcsl
Gitlab repo (`git.frama-c.com/pub/meta`) and the book-companion examples
(`git.frama-c.com/pub/frama-c-book-companion`, `high-level-properties/`). Do not
present a guessed concrete keyword as authoritative.

---

## 6. Verification by transformation (semantics)

MetAcsl proves nothing itself. With `-meta`, it **parses** the HILAREs and
**generates ordinary ACSL** that the core plug-ins then discharge. The
per-context translation:

- **`weak_invariant`** — add `P` as both a `requires` and an `ensures` of each
  target function.
- **`strong_invariant`** — as weak, **plus** insert `//@ assert P;` after every
  instruction that may modify a free variable of `P` (the AST is normalized so
  every modification is an assignment; in the presence of pointers it assumes the
  worst case about what is touched).
- **`\writing`** — before every instruction that may write memory (except calls),
  insert `//@ assert P;` with `\written` replaced by the actual l-value being
  written.
- **`\reading`** — symmetric to `\writing`, with `\read` replaced by the actual
  read location.

Once generated, run **WP** (deductive proof), **Eva** (abstract interpretation),
or **E-ACSL** (runtime checking) on the resulting annotations. Because everything
reduces to standard ACSL, MetAcsl inherits all the backends and is amenable to
both *proof* and *testing*.

A proof failure is reported at the precise generated site, with the meta-variable
instantiated — so you debug it exactly like an ordinary failed assertion.

---

## 7. Why `\writing` beats `assigns`

`assigns` cannot express two things that `\writing` can, and these are precisely
what integrity properties need:

- **Non-transitivity.** ACSL `assigns` is *transitive over calls*: if any callee
  is permitted to modify `x`, then a caller that invokes it also (transitively)
  "assigns" `x`. So `assigns` cannot say "this function must not *directly* modify
  `x`, even though it may call the one function that is allowed to." `\writing`
  targets **direct** writes, so a function may legitimately call the privileged
  modifier without itself violating the HILARE.
- **Conditional restriction.** `\writing` lets the forbidden-modification
  condition depend on state (e.g. "...only when the page is ALLOCATED"), whereas
  `assigns` has no built-in conditional mechanism.

Concretely, "only `page_encrypt` may change the confidentiality level of an
*allocated* page" is a one-line `\writing` HILARE (`M_2` above) and is not
expressible with `assigns`.

---

## 8. CLI, backends, installation

- **Activate**: pass **`-meta`** to Frama-C; it parses meta-properties and emits
  the generated ACSL.
- **Discharge**: chain a core analyzer, e.g.
  ```
  frama-c file.c -meta -then -wp -wp-rte         # generate, then prove with WP
  frama-c file.c -meta -then -e-acsl ...          # generate, then check at runtime
  ```
- **Backends**: WP, E-ACSL, Eva (any plug-in that consumes ACSL).
- **Install**: distributed separately under an open-source licence. Available via
  **opam** as **`frama-c-metacsl`**; sources on Gitlab at `git.frama-c.com/pub/meta`.
  A companion MetAcsl release exists for each Frama-C version since **22.0
  Titanium**, kept compatible with Frama-C's public repository.

---

## 9. The canonical confidentiality case study

The page-management example (Robles et al.) is the standard teaching case. Pages
carry an allocation `status` and a `confidentiality level`; a process has a
`user_level`. The desired guarantees:

- *P_write* — a user may not write data to a page of lower confidentiality than
  its own.
- *P_read* — a user may not read data from a page of higher confidentiality than
  its own.

These are expressed as `M_2` (`\writing`) and `M_3` (`\reading`) above, with
`M_1` a `strong_invariant` keeping every page's status well-formed. The
illustrative bug: in `page_alloc`, setting `status = ALLOCATED` *before* setting
`level` makes the `\writing` assertion for `M_2` fail (an allocated page's level
is being written while the separation premise already holds). The fix is to
**reorder** the two assignments. This is the archetype of MetAcsl debugging: the
plug-in pinpoints the offending write, and the remedy is a code reordering or an
added guard. A companion "smart-house manager" study expresses temporal-flavored
rules like "a door unlocks only after authentication or alarm".

The same machinery scaled to the **JavaCard Virtual Machine** verified by Thales
for **Common Criteria EAL6**, where access-control security properties were
written as meta-properties and discharged with WP alongside MetAcsl (see
bibliography).

---

## 10. When to reach for MetAcsl

Use a HILARE instead of hand-written ACSL when **any** of these hold:

- The property must be checked at **many program points** (every write, every
  read, every point) — manual assertions would be tedious and easy to miss one.
- The property spans **many functions** and is about what they may/may not *do*
  to shared state (integrity, isolation, confidentiality, access control).
- You need a **non-transitive** or **conditional** restriction on modifications
  or accesses that `assigns` cannot express.
- You want a **single auditable artifact** a certifier can read as "the security
  property", and cheap **re-verification after every code change** so the
  property cannot silently regress.

If instead the property is naturally one function's input/output behavior, a
plain ACSL contract is the right tool — don't over-reach for MetAcsl.
