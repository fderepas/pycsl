# PyCSL ownership discipline (the value-semantics boundary)

**Status:** Normative (specification) · **Implements:** `no-more-int-7.md` §A2b-1 · **Decided by:**
the §0 alias audit (`docs/pycsl-alias-audit.md` — pycsl's own source already satisfies this) ·
**Position:** `docs/handling-aliasing.md`.

This document writes down the **accept/reject rule** that has, until now, been enforced *implicitly*:
which uses of mutable objects PyCSL verifies, and which are out of scope. It is the precise statement
of the **value-semantics boundary**. Per the §0 audit it documents an *already-satisfied* discipline
rather than gating a new build — but stating it explicitly (a) lets users know the boundary, (b)
unblocks the A1-residual seq-model (it fixes the snapshot semantics), and (c) defines what a future
A2b-2 alias checker would enforce, should a third-party use case ever demand it.

## 0. Why this exists

Python has unrestricted mutable aliasing; Why3 forbids aliasing of mutable data (its region system is
why VCs stay first-order). PyCSL bridges the two by **reasoning about mutable objects only where they
behave by value** — i.e. where no two simultaneously-live references write the same object. Programs
inside this boundary verify soundly; programs outside it are out of scope (today: they verify
confusingly or unsoundly; with a future A2b-2, they would be rejected with a diagnostic).

## 1. Values: mutable vs immutable

- **Immutable** (`int`, `bool`, `str`, `float`, a record/`#@ datatype` value treated by value, `tuple`
  of immutables): may alias **freely and safely** — sharing an immutable is never observable. No
  restriction.
- **Mutable** (`list`, `dict`, `set`, a class instance with a `mutable` field): subject to the rules
  below.

## 2. The accept/reject rule

A program is **inside the boundary** iff every mutable object satisfies: *at no program point are there
two distinct live references to it that are both subsequently written.* Concretely, the following are
**accepted**:

- **(A1) Local accumulation.** Build a mutable local (`acc = []`, `acc.append(...)`) and read/return it.
  Single owner; value semantics.
- **(A2) Ownership transfer.** Pass a mutable to a callee (or return it) and **do not use the original
  binding afterward**. The callee becomes the sole owner.
- **(A3) Stack-scoped borrowing (out-parameters).** Pass a mutable to a callee that mutates it in place
  (`f(out)` with `out.append(...)`); the callee's reference dies at return; the caller resumes as sole
  owner. This is a *mutable borrow* — exactly the Creusot/Dafny-`modifies` case. The callee's effect
  on `out` is described by its `assigns` clause (now read as an *owned footprint*).
- **(A4) Snapshot-into-container** (see §3) — a mutable entering a container is copied by value.

The following are **rejected** (out of scope):

- **(R1) Shared mutable aliasing.** Two live references to one mutable object, both written
  (`a = b; a.append(1); b.append(2)`; or storing a list in a dict *and* keeping the original and
  mutating both). The interleaving is observable and not value-expressible.
- **(R2) Mutable default arguments** (`def f(x, acc=[])`) — a hidden cross-call shared object.
- **(R3) Mutate-through-alias of a stored object** — `self.x = p` (p mutable) then later `p.append(...)`
  expecting `self.x` to change.

## 3. Snapshot semantics for values entering containers — **(the A1-residual enabler)**

When a mutable value enters a container — `d[k] = xs`, `lst.append(ys)`, `self.field = zs` — it is
modeled as a **value snapshot taken at the store site**: the container holds a *copy of the value's
content at that moment*, not a live alias. Subsequent mutation of the original binding does **not**
change the stored copy (and vice-versa); such a program is outside the boundary (R3) and out of scope.

This is a **sound under-approximation**: it never proves a false postcondition, because it models
*less* sharing than Python has — a property proved about the snapshot holds for any execution where
the boundary is respected, which is the only execution PyCSL claims to verify.

**Consequence — A1-residual seq-model is unblocked.** `Dict[str, List[int]]` stores its list value as
an immutable `Seq.seq int` *snapshot* at `d[k] = xs` (array→seq at the store site); reads return the
snapshot (`Seq.length`, `Seq.get`). The mutable-array-in-a-pure-map wall does not apply, because the
stored value is the immutable snapshot, by this rule. (This was the "design question" that turned out
not to be one — it is a *consequence* of the boundary, not a separate problem.)

## 4. `self` and methods

`self` is **borrowed** for the duration of a method call (stack-scoped, like A3): the method may read,
and write within its `assigns`, the receiver's owned fields; the caller resumes as owner at return.
Returning a mutable field aliased to the receiver, then mutating both, is R1 (rejected). A method that
mutates a field through a value passed in (R3) is rejected.

## 5. Enforcement status

- **Today:** enforced *implicitly* — programs outside the boundary do not get a clean diagnostic; they
  verify confusingly or (for R-cases) potentially unsoundly. The §0 audit confirms **pycsl's own
  source is inside the boundary** (local accumulation + stack-scoped borrows + store-and-read), so
  self-hosting does not require more.
- **A crude enforcement** is cheap and worth having even short of full A2b-2: reject R2 (mutable
  default args — a pure-syntactic check) and flag `self.x = <param>` followed by a mutation of that
  param (R3 heuristic). These catch the common bugs without a full alias graph.
- **Full enforcement (A2b-2)** — a sound per-program-point alias/ownership analysis — is **contingent**
  (build only if a third-party use case needs aliased mutation that must verify). Its gates are in
  `no-more-int-7.md` §A2b-2, including the false-reject acceptance gate.

## 6. The single-backend escape valve — defined trigger

PyCSL stays single-backend (Why3) under this discipline. The escape valve to a second backend (Viper,
the Cameleer move) is reserved and **triggered only** by a *concrete driver* meeting **all three**:
(i) unavoidable **shared mutable aliasing** — two live references to one mutable object, both written,
interleaving-dependent; (ii) the property under proof **cannot be made sound by snapshot/transfer**
(it genuinely depends on the sharing); and (iii) **no proof-assistant-imported framing lemma
suffices**. Anything short of all three stays in Why3. (Recorded here so "ever needed" is enforceable,
not invoked under deadline pressure.)
