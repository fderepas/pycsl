# agent-stdlib-annotate — body-verified stdlib stubs (0 `\trusted`)

The guiding discipline for `src/pycsl_lib/` standard-library stubs and their
`*_demo.py` drivers. This is a **policy**, not a suggestion: the durable fix for
"the delegate keeps shipping unprovable stubs" lives here, in the skill — not in
hand-patching each stub.

## The rule

1. **Stubs are body-verified. Zero `\trusted`.** A stub function's body must
   prove its own contract. The cheapest case is already free: `return 0` under
   `#@ ensures \result >= 0` proves with no trust — so a stub that does this needs
   **no** `\trusted` line at all (just delete it).
2. **Model state concretely**, the way `unix-filesystem/UnixInodeFileSystem.py`
   (835 lines, 0 `\trusted`) does, and as corpus `0427`/`0428` show in miniature:
   a class with `#@ class invariant`, `self.<field>` state held in `int` / `array
   int`, methods that mutate fields and prove `requires/ensures/assigns` via array
   indexing, loop invariants, and guards. Mirror that shape for stateful stubs
   (e.g. `io.StringIO` → a buffer class with `array int` content + `pos`).
3. **For an irreducibly-opaque kernel, cite a lemma — never trust it.** Some
   operations cannot be expressed in WhyML (parsing a string into a tree, byte
   marshaling, bitwise tricks). Model these as an **abstract `val`** (a bodyless,
   uninterpreted declaration — `module6_whyml/abstract_ops.py:_add_abstract_op`)
   carrying an `ensures`, and pin that `ensures` with a named
   `#@ proof rocq <Lemma>` / `#@ proof lean <Lemma>` citation registered in
   `module6_whyml/preamble.py:_AXIOM_REGISTRY`. This is sound, opaque, and
   **auditable** — a different mechanism from `\trusted` (which silently assumes
   the whole contract). `\trusted` hides the trusted core; a citation *names* it.
   `unix-filesystem` does exactly this for `struct.unpack` (`UnixFs.Struct.i18.round_trip`)
   and bitwise ops (`UnixFs.Bitmap.bit_and_one_in_zero_one`).
4. **Every stub ships a property-proving `<mod>_demo.py`.** A formal driver is a
   set of **annotated functions with contracts** (`requires/ensures/assigns`), each
   discharged from its callees — NOT a module-level `print` script. `os_demo.py` is
   the template. The demo proves a property of the stub, end-to-end, with 0 `\trusted`.

## "0 trusted" ≠ "0 axioms"

The goal is **zero `\trusted`**, not zero assumptions. Genuine opacity (a string
parser, an external format, hardware) reduces to a small, **named, cross-validated
Rocq/Lean lemma** at the boundary — the auditable trusted core, stated explicitly.
That is the whole point: replace blanket trust with a citation a reviewer can check.

## Enforcement

- `bin/check-no-trusted-stubs.py` reports every `#@ \trusted` under `src/pycsl_lib/`
  (informational census tree-wide; `--strict <files>` hard-fails the named stubs).
  A migrated stub must pass `--strict`. Wired into the feature-supervisor gate.
- `bin/generate_lib_stubs.py` no longer emits `#@ \trusted` by default; newly
  generated stubs are body-verified (or carry a `# TODO: body-verify or cite axiom`
  marker, never silent trust).

## When you hit a wall

If a stub body won't prove: **do not** add `\trusted`. Either (a) strengthen the
model (more concrete state / a loop invariant), or (b) isolate the opaque step
behind an abstract `val` + a cited `#@ proof rocq/lean` lemma. See
[`pycsl-annotate/references/forbidden-expressions.md`](../pycsl-annotate/references/forbidden-expressions.md)
and [`stdlib-stub-awareness.md`](../pycsl-annotate/references/stdlib-stub-awareness.md).
