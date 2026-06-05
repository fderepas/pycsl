---
name: agent-stdlib-annotate
description: >-
  The policy for body-verified PyCSL standard-library stubs in `src/pycsl_lib/`
  and their `*_demo.py` formal drivers: every stub function proves its own
  contract with ZERO `\trusted`, stateful stubs model state concretely (class
  invariant + `int`/`array int` fields, the `UnixInodeFileSystem.py` shape), and
  an irreducibly-opaque kernel becomes an abstract `val` pinned by a cited
  `#@ proof rocq|lean` lemma — never `\trusted`. Use whenever writing, fixing, or
  reviewing a stdlib stub or its demo, deciding between `\trusted` / `\abstract` /
  a cited axiom, or diagnosing why a delegate keeps shipping unprovable stubs.
---

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

If a stub body won't prove: **do not** add `\trusted`. In order of preference:

1. **Strengthen the model** — more concrete state, a loop invariant, a richer field.
2. **`#@ \abstract`** (annotations.md §2.1.14) — for an *irreducibly-opaque* op, mark
   the function `#@ \abstract`: it emits a bodyless `val` defined solely by its
   contract (sound, uninterpreted). Unlike `\trusted` it is NOT a trusted, present-but-
   unchecked body — there is no body; the contract IS the definition. It passes
   `check-no-trusted-stubs`. This is the canonical 0-`\trusted` model for a parser,
   an external format, a hardware primitive. Example — `ast.literal_eval` (which IS
   Python's parser): an `#@ \abstract` `val` with a bounded raises set
   (`ValueError`/`SyntaxError`), so a `try/except` wrapper around it is provably total
   (corpus `0449`), even though its parsed value is uninterpreted.
3. **Pin a real fact with `#@ proof rocq/lean`** — if there is a genuine, non-trivial
   property of the opaque op (a round-trip, an algebraic law), cite a cross-validated
   lemma in `_AXIOM_REGISTRY` and consume it. `unix-filesystem` does this for
   `struct.unpack` / bitwise ops. **Do not** invent a tautological or value-specific
   "axiom" just to have one — a rubber stamp is worse than an honest `#@ \abstract`
   spec. If the only true fact *is* the contract (as for `literal_eval`'s value),
   stop at step 2.

## Runtime decoration is tolerated, never verified

`print(...)`, f-strings (`f"…"`), and `type(x)` carry **no** proof obligation and no
observable `assigns` effect: a verified function that uses them proves exactly as if
they were absent (their results are discarded or bound to unused locals). They are
**tolerated decoration** so a literal demo parses — but their results must **never**
feed proven content (a `type(x)` value used in a contract would be an opaque, unsound
spot). Keep them out of the verified surface. Corpus `0450` locks this.

`SyntaxError` is a first-class **explicit** exception — `#@ raises SyntaxError`,
`raise SyntaxError`, and `except (ValueError, SyntaxError)` all work (the preamble
declares any exception named in a `raises` contract or handler). It is deliberately
**not** in `exception_model.KNOWN_EXCEPTIONS`, which is reserved for exceptions with a
mathematical *implicit trigger* (ZeroDivision/Index/Key/Value/StopIteration); a
parse-time error has no such trigger.

See
[`pycsl-annotate/references/forbidden-expressions.md`](../pycsl-annotate/references/forbidden-expressions.md)
and [`stdlib-stub-awareness.md`](../pycsl-annotate/references/stdlib-stub-awareness.md).
