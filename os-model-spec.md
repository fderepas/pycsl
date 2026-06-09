# os-model-spec.md — functional-correctness specification for the os model

**Status:** Specification (properties only — no implementation choices)
**Date:** 2026-06-09
**Goal:** extend the verified os model so it proves **functional correctness** — that a file
faithfully stores and returns its content, and is retrievable by name — not only the safety and
return-code contracts it proves today.

---

## 1. Why this specification exists

The os module currently proves **0 unproven goals**, but the contracts being discharged are
**safety- and structure-level**: array accesses are in bounds, the disk-length and fd-column class
invariants are preserved, every syscall returns a well-formed code (`0`/`-1`, an fd `>= 3`, a count
`<= n`). These are real guarantees — the os cannot crash, corrupt its layout, or return a malformed
result.

They are **not functional correctness.** Two observations make the gap concrete:

- The existing round-trip driver asserts only `\result == 0 or \result == 1`. That postcondition is
  satisfied *even if every operation fails* — it proves the function terminates with a well-formed
  code, not that a file round-trips.
- A content round-trip — *write `c` to file `f`, close, reopen `f`, read it back, and observe `c`* —
  is **not even expressible** against the present API: `read` returns a byte **count**, never the
  bytes. And directory names are stored opaquely (the encoded name is modeled as an unspecified
  buffer), so a reopen cannot be shown to resolve back to the file just created.

This specification defines the behaviour the model must guarantee so that the content round-trip
becomes a *provable* property. The driving acceptance test is `pure_lib_test/formal_0008.py`
(create `f`, write `c`, close; reopen `f`, read; `#@ ensures \result == True`).

## 2. Scope

**In scope** — the observable functional behaviour of a regular file and the directory that names it:

- the **content** a file stores and returns across read/write;
- the **name → file** mapping the directory maintains across create/open/unlink;
- the **persistence** of both across close and reopen.

**Out of scope** (named here so the boundary is explicit, not silent):

- timestamps, permission semantics beyond what return codes already encode;
- multi-process / concurrency behaviour;
- the symlink *target* content (only its presence/type, already modeled);
- performance, on-disk format compatibility with a real kernel.

The initial acceptance target is the **single-data-block** case (content up to one block); the
properties below are stated generally, and the multi-block generalisation is a later increment under
the same properties.

## 3. The correctness properties

These are stated as observable round-trip properties over the public os operations, for an arbitrary
filename `f` and content `c` within the stated bounds. They are the *what*; §5 lists what the model
must therefore expose or preserve, still without prescribing *how*.

- **P1 — Content fidelity (write then read).** Given a descriptor open for writing at offset 0 of a
  regular file, after a `write` that reports it stored all of `c`, a read of `len(c)` bytes from
  offset 0 of that file yields a buffer **equal to `c`**, byte for byte. Content that is written is
  the content that is read.

- **P2 — Name resolution (create then open).** After an operation that creates a file named `f` and
  succeeds, a subsequent open of `f` resolves to the **same file** (same inode) as the one created.
  Distinct names resolve to distinct files; an open of a name never created (and not since removed)
  does **not** resolve to an unrelated file.

- **P3 — Persistence (close then reopen).** Closing a descriptor and reopening its file by name
  preserves both the file's **content** (P1 still holds afterward) and its **identity** (P2 still
  holds afterward). Close/open do not disturb stored data or the name mapping.

- **P4 — Composite round-trip (the acceptance property).** The composition of P1–P3: *create `f`,
  write `c`, close; reopen `f`, read `len(c)` bytes; the result equals `c`* — holds for all `f` and
  all `c` in range, and the driver expressing it provably returns `True`. This is exactly
  `formal_0008`.

A property is only meaningful if its **failure is expressible**: the model must be able to *observe*
content and identity (so a wrong byte or a misresolved name would make the postcondition fail to
prove), not abstract them away such that the property holds vacuously.

## 4. Faithfulness requirements

The properties above must be achieved by **value-modeling the byte content** that the round-trip
observes — file data and directory names — not by widening contracts or asserting unproven identities.
Concretely, as constraints on any implementation:

- **No opacity where the property observes content.** The bytes of file data, and the bytes of a
  stored directory name, that P1–P4 depend on must be tracked as values in the logical model. Where
  today they are modeled as unspecified buffers (the "encoded content is opaque" boundary), they must
  become value-determined for the structures the round-trip touches. Opacity may remain only for
  content **no property observes**.

- **Semantics stay faithful to real behaviour.** Operations keep their true partiality — e.g. a
  packer that rejects out-of-range input still rejects it; an open that can fail still can. P4's
  `\result == True` is earned by the driver establishing the success preconditions, never by
  pretending an operation is total or infallible. (This is the same faithfulness bar applied
  throughout: model the real semantics, do not coerce them for convenience.)

- **No new trusted axioms.** The properties must be discharged by the SMT backend from
  value-level reasoning. The os trusted-axiom base must remain a single cross-validated family
  (the bitwise bound); P1–P4 must not (re)introduce a codec round-trip axiom. If a sub-property is
  genuinely beyond SMT reach, that is a finding to surface and justify explicitly, not a default.

## 5. What the model must expose or preserve (requirements, not design)

Derived from §3–§4, still implementation-agnostic:

- **An operation that returns read content.** P1 requires that content be *observable*; the model
  must offer a read whose result is the bytes read (a buffer), distinct from the byte-count report
  that exists today. (Whether this replaces or supplements the current read is a design choice for
  the next phase.)

- **A by-value name → inode association.** P2 requires that a stored name be compared and resolved by
  its value, so that "the name I created" and "the name I open" are provably the same entry, and
  different names are provably different.

- **A framed-persistence guarantee across close/open.** P3 requires that the operations between the
  write and the read (close, open, seek) provably leave the file's data region and the directory's
  name mapping unchanged — i.e. their frames exclude the bytes the round-trip depends on.

- **Established success preconditions for the round-trip.** P4 requires the driver to be able to
  discharge the conditions under which create/open/write/read succeed (a free filesystem has capacity;
  a just-created name resolves), so the success path is provably taken.

## 6. Acceptance criteria

The work is complete when **all** hold:

1. `pure_lib_test/formal_0008.py` proves (`\result == True`, *Valid*) for symbolic `f` and `c` in the
   stated bounds.
2. The full os module proof (`pure_lib/os/__init__.py`) remains at **0 unproven goals**, and
   `formal_0001` still passes — no safety/structural regression.
3. The os **trusted-axiom base stays one family** (the bitwise bound); no round-trip axiom is
   reintroduced.
4. The reference corpus stays byte-clean for files the change does not intend to alter; doc-coherency
   stays green.
5. The properties P1–P3 are each exercised by a driver whose postcondition would **fail to prove** if
   the corresponding fidelity were violated (the "failure is expressible" check of §3), so P4 is not
   passing vacuously.

## 7. Non-goals

- Replacing the existing safety contracts — they remain and must keep proving.
- A bit-for-bit emulation of a real kernel's on-disk format or error taxonomy.
- Closing the content-opacity boundary for structures **no functional property observes** (those may
  stay abstract).

## 8. Invariants the change must keep

The class invariants the os already proves (disk-length lower bound, fd-column lengths, non-negativity
of credentials and clock) and the no-crash/in-bounds guarantees must be preserved at every step;
each increment is gated on the full os proof holding at 0 unproven before it is committed.
