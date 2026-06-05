# Comments on `mixin-specification.md`

*Balanced review. Grounded where possible in PyCSL's actual mixin code — the
`module6_whyml/` emission mixins and the `module5/` package, which were just
decomposed into the very shape this spec is about (Part B refactor: facade +
sibling mixins, MRO dispatch, byte-identical emission).*

## Overall assessment

This is a thoughtful, literature-grounded proposal. The diagnosis is right: the
hazards of Python mixins — silent field collisions, undeclared interface
dependencies, MRO picking a method-conflict winner silently, and retroactive
contract modification — are real bug sources, and a verifier *can* enforce a
discipline the runtime doesn't. The trait-calculus framing (Schärli/Ducasse,
Damiani 2014 incremental proof, behavioral subtyping) is apt, the annotation
surface is small and consistent with PyCSL's erase-at-runtime model, and
Example 6's honesty about what the discipline *can't* do (introspection-based
mixins) is exactly the right intellectual posture.

My reservations are not about the idea but about **fit to PyCSL as it actually
is** and about **rigor in the parts the examples skip**. In short: the proposal
is strongest as a general trait system and weakest as a response to a concrete
PyCSL need — and PyCSL's own methodology (demand-driver first; expand a real
type/feature only where a verification-grade program fails today) would ask for
that need to be named before building seven directives and a new pass.

## What's genuinely strong

- **Incremental verification is the real prize.** "Verify each mixin once
  against its declared interface; re-check only the resolution moves on
  composition" (Damiani 2014) is a property worth having, and the spec states it
  cleanly.
- **The conflict-resolution rule (Example 3) is correct and valuable in
  principle.** Forcing `resolve`/`exclude` instead of letting C3 pick
  left-to-right silently is the kind of "no silent semantic change from
  refactoring base-class order" guarantee that prevents a whole class of bugs.
- **The required-method/abstract-operation shape (Example 5) is the right model
  for reusable mixins**, and it dovetails with work PyCSL already has (see the
  RT note below).
- **Example 6 is the most useful page.** Naming the exact patterns that *don't*
  fit (`dir`/`setattr`/`__getattribute__` cross-cutting concerns) and showing
  the disciplined rewrite is honest and actionable.

## Where the model clashes with PyCSL's actual mixins

This is the load-bearing comment, and it comes straight from the code just
refactored.

**1. PyCSL's real mixins share facade state pervasively — the `touches_field`
disjointness rule would flag the entire architecture.** The spec's clean
examples give each mixin disjoint, owned fields (`_count`, `_log`, `_items`).
PyCSL's emission mixins do the opposite by design: `ExpressionEmissionMixin`,
`StatementEmissionMixin`, `PreambleEmissionMixin`, the new
`GhostCollectionOpsMixin`/`stmt_control_flow`/`module5/*` siblings, etc., all
read and write a large *shared* facade state — `self.program_ir`,
`self._in_spec`, `self._array_locals`, `self._dict_locals`, `self._record_types`,
`self._current_self_type`, `self._ghost_string_vars`, … none of which is "owned"
by one mixin. Under rule 1 ("no two mixins touch the same field without explicit
resolution") this legitimate, intentional design reads as one enormous
unresolved field conflict. Either the rule is too strict for the facade-with-
shared-state pattern PyCSL actually uses, or PyCSL must emit dozens of
`touches_field` + resolution clauses for state that is *meant* to be shared.
The spec's "self-hosting case is comfortable" claim under-weights this; the
self-hosting mixins are conflict-free on *method names* but maximally entangled
on *fields*.

**2. The hard PyCSL case is shared *concrete* helpers, which the
provides/requires_method dichotomy doesn't cleanly cover.** PyCSL's sub-mixins
don't implement an abstract interface the composer fills in (the `requires_method`
shape). They call *concrete* helpers that live in the core mixin and are resolved
by MRO: `GhostCollectionOpsMixin._handle_map_get_expr` calls `self._e` /
`self._deref`; `stmt_control_flow` handlers recurse into `self._stmts_to_whyml`;
all handlers are reached by `getattr(self, _EXPR_DISPATCH[t])` /
`_STMT_HANDLERS[s]` tables that stay on the core. That is neither "provides"
(the sub-mixin doesn't own `_e`) nor "requires_method" in the abstract-operation
sense (it's a concrete dependency on a sibling, not a hole the composer fills).
The spec needs a third relation — *concrete cross-mixin dependency* — or its
verifier will either reject PyCSL's own composition or be forced to treat every
shared helper as an abstract requirement, which is a lot of contract restatement.

**3. Trait-flattening vs MRO.** The spec wants order-independent flattening with
explicit resolution; Python (and PyCSL's facade) resolves by C3 MRO. The
"composition pass after MRO computation" has to reconcile these, and the corner
that bites PyCSL is precisely the shared-helper case in (2): `_e`/`_deref`/
`_stmts_to_whyml` are provided once by the core and *depended on* (not
overridden) by siblings — fine under MRO, but the spec's exclusive-`provides`
model has no vocabulary for "concrete method many mixins lean on." Worth
specifying how a method that is provided once and called by N siblings is
distinguished from a genuine N-way conflict.

## Where the examples overstate what PyCSL can discharge today

The verification-obligations boxes repeatedly say "Why3 discharges this
trivially," but several example contracts are **not dischargeable under PyCSL's
current models** — and the methodology's own rule ("don't oversell; set doc
expectations to the real reach") argues for flagging that:

- **`\old` of a whole collection.** Examples 2–6 lean on
  `ensures self._X == \old(self._X) + [item]` / `... + [message]`. PyCSL today
  does **not** support `\old(arr)` for a whole array/list — only `\old(scalar)`
  and `\old(arr[i])` (see `annotations.md` and the transpiler-limits skill). So
  the append-content postconditions in Examples 2, 3, 4, 6 are aspirational, not
  "trivial."
- **`str(int)` content.** Example 4's `["start at " + \str(now)]` and
  `["op " + \str(\old(self._count))]` require reasoning about the *content* of an
  int rendered to string. PyCSL's string model treats `str`/`\str` of a non-literal
  as opaque (no code points, no `ord`); that concatenation's content is not
  modelable, so those `ensures` clauses cannot be proven as written.
- **`\old(\result)` as a determinism encoding (Example 5).** This is a novel,
  non-standard use of `\old` (a result has no pre-state value). It needs a real
  semantics, not a hand-wave. Notably, PyCSL **already has** the property this is
  trying to express: referential transparency, which the pipeline *infers* for
  `@lru_cache` soundness (UB-7.7: pure + reads no mutable `#@ shared`). The
  `Cached` mixin's "deterministic + pure `compute`" requirement is exactly RT.
  The spec should reuse PyCSL's existing RT notion (and its `let function`
  emission, which gives `f x = f x` for free) rather than invent `\old(\result)`.

None of these sink the proposal, but presenting unprovable contracts as
"discharged trivially" undersells the work and will mislead an implementer about
scope.

## On the `__init__<mixin>` convention

Hand-chaining `self.__init__counting()` / `__init__loggable()` from the composer's
`__init__` re-implements constructor chaining manually to avoid `super().__init__`.
It is provable (a missing call surfaces as an unestablished class invariant —
good), but it is also an error-prone protocol: the composer must remember to call
*every* mixin's init, and nothing in the surface *requires* it except the
downstream invariant failure. Consider making `compose_from` generate the
obligation "the composer's `__init__` must call each composed mixin's init-hook"
as a first-class, named check, rather than relying on an invariant to fail later.

## Process / scoping comment (PyCSL's own discipline)

By the project's gating discipline — which I just wrote into
`pycsl-how-to-develop` §8 — a capability this size wants (a) a named
**demand-driver**: a verification-grade program that fails today *because* mixin
composition is unchecked, and (b) **tiering** by feasibility. The spec's own
admission that "pycsl's own mixin use is exactly the textbook kind" (Examples 1–2:
no conflicts, no diamonds) is the tell: the **self-hosting need is a small
subset** — `#@ mixin` + `provides` + a *shared-state-aware* `touches_field` +
init-hook checking — while the conflict/diamond machinery (`resolve`/`exclude`,
Examples 3–4) targets hypothetical general code PyCSL does not contain. A
demand-driven plan would build the subset that makes PyCSL's *actual* facade
mixins checkable (which first requires resolving concern #1/#2 above), commit it
behind a `# pycsl-expected: FAIL` driver, and gate the rest until a real program
needs it.

## Suggested next step

Before any implementation, write one PyCSL file that **fails today** for want of
this discipline and would **pass** with it — and make it one of PyCSL's own
emitter mixins, since those are the self-hosting target. That exercise will force
the spec to confront the shared-facade-state reality (concerns 1–3) up front,
which is where the real design work is. The clean six examples are a good
north-star; the messy real mixin is the demand-driver.

## Bottom line

Conceptually sound and well-referenced; the discipline is genuinely valuable for
the general mixin problem and Example 6's honesty is a model. The gaps are
fit-to-PyCSL (the facade's shared mutable state and concrete shared helpers don't
match the disjoint-fields / abstract-requires_method model), a few examples that
claim dischargeability PyCSL doesn't yet have (`\old(collection)`, `str(int)`
content, `\old(\result)`), and the absence of a named demand-driver to right-size
the build. Resolve the shared-state question and reuse the existing RT machinery,
ground it in a failing self-hosting driver, ship the minimal subset first — and
this becomes a strong, PyCSL-shaped feature rather than a general trait system
bolted on.
