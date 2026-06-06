**Backend-as-enforcer** is the design principle that, for certain
soundness-critical properties, PyCSL **emits the construct and relies on Why3 to
reject the bad case at verification time**, rather than duplicating the check as a
Module-4 pre-pass. The backend is the authority; a PyCSL pre-check would at best be
an earlier, cleaner diagnostic — never the thing that closes the hole.

---

## Where the principle applies

- **Termination of recursive lemmas / functions.** PyCSL does *not* require
  `#@ \variant`. Why3 infers a structural variant and rejects ill-founded recursion
  via its termination VC, so a non-terminating "[lemma](lemma-function.md)" cannot
  export `False`. (Requiring the annotation was redundant *and* over-restrictive —
  it rejected provable lemmas. This was "decision A".)
- **[Strict positivity](strict-positivity.md)** of inductive predicates — Why3
  rejects `non strictly positive occurrence …`.
- **Typed quantifier binder *use*** — misusing a datatype binder (arithmetic on it)
  is caught by Why3's typechecker; PyCSL only checks the binder *type* resolves.
- **Contract-call-position** — using a `let lemma` as a term in a contract is
  rejected by Why3 (a lemma is not a usable term).

## Why not always pre-check?

Each pre-check is extra code that can *itself* be wrong (and silently so — a
[load-bearing](load-bearing.md) risk). When the backend already enforces the
property soundly, a redundant PyCSL gate adds surface without adding safety, and an
*over-strict* gate rejects valid programs. The discipline is to add a pre-check
only for diagnostics or for a hole the backend does **not** close.

## The contrast: gaps the backend does NOT close

Some properties Why3 cannot see, so PyCSL *must* enforce them — e.g. a
`#@ lemma` body may not call a `\trusted` function (the trusted `val`'s contract is
axiomatic, so Why3 would accept the leak). Those *are* Module-4 checks. The
principle is about knowing which side of the [trust seam](trust-seam.md) each
property sits on.
