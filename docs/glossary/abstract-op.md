An **abstract op** (declared with `#@ \abstract`) is a function modeled as a **bodyless WhyML
`val` defined solely by its `ensures` contract** — an uninterpreted operation whose specification
*is* its definition.

It is the sound counterpart of a [trusted stub](trusted-stub.md). Both emit a `val` with no body,
but they trust differently:

- A **trusted stub** (`#@ \trusted`) *assumes an unchecked body satisfies its whole contract* — the
  body exists and is simply not proved.
- An **abstract op** (`#@ \abstract`) has **no body to check** — there is nothing unverified; the
  contract is the entire, honest definition. It therefore does **not** count against the
  "0 `\trusted`" policy and passes the no-trusted-stub lint.

---

## Why abstract ops matter in PyCSL

Some operations are irreducibly opaque whatever the value domain (int, string, array, map, …) — parsing a string into a tree
(`ast.literal_eval`), byte marshaling (`struct.unpack`), bitwise tricks. PyCSL cannot model their
internals soundly, so faking a body would be dishonest. The honest boundary is to declare them
abstract: an uninterpreted `val` that says only what its contract states.

The safety model is the abstract op's **bounded `raises` set**: callers reason about which
exceptions it may raise (so a `try/except` wrapper can be proved total), without assuming anything
about the unconstrained result. When a *non-trivial* fact about the result is genuinely needed, the
abstract op's `ensures` is pinned by a **cited cross-validated lemma** —
`#@ proof rocq|lean <Lemma>` registered in the axiom registry, where the witness Rocq/Lean theorem
closes by an honest proof (no `Axiom`, no `Admitted`). "0 `\trusted`" is not "0 axioms": the cited
set is the explicit, auditable [trusted computing base](trusted-computing-base.md), named rather
than hidden.

This is the mechanism behind the standard-library stub discipline (prefer `\abstract` + a cited
lemma over `\trusted`) and behind modeling an irreducible parser as `\abstract` rather than letting
its trust vanish.

---

## Concrete examples

### Opaque kernel with a bounded raises set

`ast.literal_eval` is Python's parser — irreducible. Modeled as `#@ \abstract` with a documented
`raises { ValueError, SyntaxError }`, a `try/except` around it is provably total, with no `\trusted`.

### Abstract op pinned by a cited lemma

`struct.unpack(">H30s", data)` is an abstract `val` whose round-trip `ensures` is pinned by
`#@ proof rocq UnixFs.Struct.i18.round_trip`, whose Rocq witness closes by `reflexivity` (the
legacy, UNGUARDED shape-model — the byte content is uninterpreted).

A WHITELISTED scalar shape is instead lowered to the **faithful, guarded** `Pycsl.Struct.Std`
family with a **per-field width/signedness tag** (`struct_{pack,unpack}_f<tag>` — `fu16`, `fu32`,
`fi16`, `fi32`, `fi64`, `fu16u32`, `fi32i32`, `fs4`): the abstract `val` carries a size-law
`ensures` and a per-field in-range `requires`, and its round-trip is pinned by
`#@ proof rocq|lean Pycsl.Struct.Std.round_trip_<tag>` whose Rocq+Lean witnesses give pack/unpack a
CONCRETE base-256 byte-codec definition (signed via two's complement, multi-slot via disjoint-byte
concatenation) — so the round-trip is a real theorem and the guard is proven load-bearing
(`unpack(pack 65536) = 0 ≠ 65536`; `unpack(pack 32768) = -32768 ≠ 32768`), not a `reflexivity` over
uninterpreted symbols. The per-field tag also makes `'>HH'` and `'<ii'` distinct symbols (no more
`struct_pack_i2` collision). See `docs/glossary/axiom-registry.md` and UB catalog §7.4a–c.

### Val-bridge

A logic-only Why3 symbol (e.g. `String.length`) that cannot appear in a program context is bridged
through an abstract `val str_length_op (s: string) : int` whose `ensures` ties its result to the
logic symbol — the recurring technique for promoting a real type (strings, floats).

---

## Related terms

- [trusted stub](trusted-stub.md)
- [trusted computing base](trusted-computing-base.md)
- [trust seam](trust-seam.md)
- [proof companion](proof-companion.md)

> **In short:** an abstract op is a bodyless `val` defined entirely by its contract — sound and
> opaque, with nothing unverified to trust, unlike a trusted stub whose unchecked body is assumed.
