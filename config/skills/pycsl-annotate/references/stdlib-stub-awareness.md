# Stdlib stub awareness

Load when annotating a function that calls a Python stdlib API
and you need to know how PyCSL models the call.

> **Rulebook:** `config/skills/pycsl-stdlib-coverage/SKILL.md` is the
> normative reference for the three-artefact discipline
> (`calls-english.md`, `calls-pycsl.md`, `src/pycsl_lib/`), the
> discovery tool, the check loop, and the CPython version-bump
> workflow. This file is the annotator-workflow summary only.

Calls to standard-library APIs resolve through PyCSL's import
resolver to the **standard-library models** under `src/pycsl_lib/`, consumed as
trusted stubs at the import boundary. **Those models are body-verified — 0
`\trusted`** (see [`../../pycsl-stdlib-coverage/SKILL.md`](../../pycsl-stdlib-coverage/SKILL.md)):
each function proves its own contract (`return 0` already proves
`ensures \result >= 0`), state is modeled concretely like
`unix-filesystem/UnixInodeFileSystem.py`, and an irreducibly-opaque
kernel uses an abstract `val` + a named `#@ proof rocq/lean` citation,
never `\trusted`. *(The old generated stub set that still carried `\trusted` was
retired to `attic/pycsl_lib/`; the promoted library is body-verified.)*
Practical implications for annotating a function that calls stdlib:

- **A result carries its faithful type class — not a universal `int`.**
  Per the no-more-int doctrine a value lowers to its true WhyML type:
  `str`→`string`, `list`→`array`, `dict`→`map`, `float`→`real`, structured
  or enum values to a `record`/`variant`. Genuinely-integer results stay
  `int` — `len(x)` is an array length (`\result >= 0`), and a predicate like
  `os.path.exists(p)` is a 0/1 boolean. An irreducibly-opaque handle (e.g. a
  compiled `re` pattern) is an abstract `val`, **not** an int hash.
- **The stub's postcondition propagates automatically** — restate the stub's
  own postcondition rather than re-proving it, in the result's faithful type:
  `#@ ensures \result >= 0` after an `int`-returning size/count call; a
  `\length(\result)` / content fact after a `string`-returning call like
  `json.dumps(obj)` (its result is a `string`, **never** `\result >= 0`); an
  array-length fact after a list-returning call. Don't re-prove what the stub
  already states, and don't coerce a non-`int` result to an integer to state it.
- **Bare imports are fine.** `import os.path` resolves against the
  stub set; the pipeline never executes or fully parses CPython.

When a function uses an API with no existing stub, the annotator
has two options:

1. Body-verify the using function (the default). If a stdlib result
   feeds a postcondition you cannot discharge, isolate the opaque step
   behind an abstract `val` + a cited `#@ proof rocq/lean` lemma — not
   `\trusted`.
2. Add the entry to the three-artefact set
   (`calls-english.md` + `calls-pycsl.md` + a stub under
   `src/pycsl_lib/`). Required when the call appears frequently or
   when the surrounding module is a self-annotation target.

Consult the stdlib-coverage skill before option 2 — it governs the
check loop and the `raises` integration with `no_exception`.
