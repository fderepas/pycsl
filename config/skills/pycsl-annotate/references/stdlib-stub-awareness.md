# Stdlib stub awareness

Load when annotating a function that calls a Python stdlib API
and you need to know how PyCSL models the call.

> **Rulebook:** `config/skills/pycsl-stdlib-coverage/SKILL.md` is the
> normative reference for the three-artefact discipline
> (`calls-english.md`, `calls-pycsl.md`, `src/pycsl_lib/`), the
> discovery tool, the check loop, and the CPython version-bump
> workflow. This file is the annotator-workflow summary only.

Calls to standard-library APIs resolve through PyCSL's import
resolver to **curated stubs** under `src/pycsl_lib/`. **Stubs are
body-verified — 0 `\trusted`** (see
[`../../agent-stdlib-annotate/SKILL.md`](../../agent-stdlib-annotate/SKILL.md)):
each function proves its own contract (`return 0` already proves
`ensures \result >= 0`), state is modeled concretely like
`unix-filesystem/UnixInodeFileSystem.py`, and an irreducibly-opaque
kernel uses an abstract `val` + a named `#@ proof rocq/lean` citation,
never `\trusted`. *(Legacy generated stubs may still carry `\trusted`;
they are being migrated — `bin/check-no-trusted-stubs.py` tracks them.)*
Practical implications for annotating a function that calls stdlib:

- **Stub returns are `int`-valued in the model.** `os.path.exists(p)`
  returns 0 or 1; `re.compile(p)` returns an opaque non-negative
  integer; `len(x)` returns array length or `iter_length`.
- **The stub's postcondition propagates automatically** — claim
  `#@ ensures \result >= 0` after `return json.dumps(obj)` because
  the stub's postcondition already guarantees it. Don't re-prove
  what the stub already states.
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
