# The conversion population is 61, not 410 — 238 of the candidates are facades

**Generation #31, 03:36Z. Measured, not estimated.** A static census over the 410 STRICT
`\trusted` conversion candidates, cross-referencing each mirror body against its live twin:

| mirror body vs live | count | can it ever land? |
|---|---|---|
| **VERBATIM** (live body is, or contains, the mirror body) | **61** | yes |
| **FACADE** (`pass`, `return None`, `return <literal>` — nothing else) | **238** | **no** |
| **DIFFERS** (a real body, but not the live one) | **109** | **no, not as written** |
| mirror-missing | 2 | n/a |

## Why a facade can never land

`bin/check-self-annotate-sync.sh` states the mirror's load-bearing invariant in its own header:

> The mirror is HETEROGENEOUS: un-`\trusted` methods are **verbatim copies** of the live
> emitter (+ `#@` annotations), while `\trusted` methods are intentionally-divergent bodyless
> stubs.

Removing the `#@ \trusted` marker from a facade moves it into the un-trusted population, where
the fidelity plane demands its body equal the live body. `pass` does not equal a 200-line
parser. The conversion fails the FIRST plane it reaches, before a prover is ever started.

So a facade is not a candidate that is *hard* to convert. It is not a candidate at all. The
work it needs is not a proof — it is a PORT: copy the live body into the mirror, and only then
ask whether it lowers.

## What this invalidates, and what it does not

**Invalidated: the screen's LOWERS verdict on a facade.** The conversion screen runs
`convert_one.py` (which deletes the marker and nothing else) and then Module 6 in `--no-proof`
mode. Over a facade it is asking *"does `pass` lower and typecheck?"*, and the answer is
of course yes. Three of the five LOWERS hits found so far are exactly this:

    frontend/Module2_Parser.py  _parse_quantifier   body: `pass`        FACADE
    frontend/Module2_Parser.py  _try                body: `pass`        FACADE
    frontend/Module2_Parser.py  parse_contract      body: `return None` FACADE

Only `frontend/Module2_Parser.py::__init__` is verbatim in that file.

**Not invalidated: the two headline stubs.** The census is validated by the two cases already
worked by hand, and it agrees with both:

    errors.py::message                        VERBATIM  -> converts, proves, check 1 PASSES
    audit_proof_reverify.py::_cache_root      VERBATIM  -> converts, proves, check 1 FAILS

Neither is a facade, which is why both got as far as a real emit-diff.

## Where the 61 are

    20  pycsl.py                       3  errors.py
    11  audit_proof_reverify.py        2  proof_axiom_allowlist.py
     9  audit_proof.py                 1  each: proof2why3/sertop.py, module6_whyml/statements.py,
     6  Module6_WhyMLTranspiler.py              ir_schema.py, frontend/Module5_IREmitter.py,
     4  frontend/pure_ast.py                    frontend/Module2_Parser.py, exception_model.py

The concentration is the point: the six mirror files that were ported most faithfully hold 54
of the 61. The four big frontend modules — `Module1_Ingestor`, `Module2_Parser`,
`Module3_Weaver`, `ir_resolve` — contribute **one** candidate between them, because their
`\trusted` stubs are facades almost without exception.

## The screen was re-targeted, not restarted

At 03:36Z the running screen was stopped by its sentinel (`touch $S/STOP_SCREEN` — never
`pkill -f`, wall-lesson (c6)) with 101 of 404 done, and re-queued on the **58** verbatim
candidates it had not yet reached. That is not a small saving: the screen spends roughly
5 seconds per candidate, and 303 of the remaining 404 were unlandable by construction.

## The number that should be reported

The campaign's headline metric is 460 `\trusted` marker lines, of which 417 have a live
counterpart. **The count of markers that a proof alone can retire is 61.** The other 356 need
a port first, and a port is a different and much larger kind of work — it is the thing the
mirror's authors deferred, one stub at a time, for a reason each time.

## The second wave: 11 of the 109 DIFFERS are stale copies, not facades

`DIFFERS` is not one population. Scored by `difflib` similarity of the mirror body to the live
body:

| similarity | count | what it is |
|---|---|---|
| >= 0.95 | 3 | a stale copy — live drifted after the port, or the port dropped a line |
| >= 0.80 | 8 | a real port with a deliberate simplification |
| >= 0.50 | 9 | half a port |
| < 0.50 | **89** | a different program |

The eleven at >= 0.80, in order:

    0.991  pycsl.py                    _dispatch_provers
    0.981  pycsl.py                    _probe_one                    (and it is NESTED)
    0.980  pycsl.py                    _run_vacuity_gate
    0.937  pycsl.py                    _record_answer
    0.906  Module6_WhyMLTranspiler.py  _emit_prefunctions_infra
    0.891  pycsl.py                    _parse_args
    0.868  Module6_WhyMLTranspiler.py  _wrap_call_with_callee_raises_assert
    0.854  audit_proof_reverify.py     verify_lean_file
    0.828  pycsl.py                    _run_proofs
    0.824  pycsl.py                    _resolve_runtime_config
    0.805  Module6_WhyMLTranspiler.py  __init__

So the honest bracket for "retirable by proof, with at most a small mechanical re-port" is
**61 to 72 of 410** — and 89 of the 410 are a different program in the mirror than in the live
tree, which is the population `finding-a-verified-program-that-is-not-the-executed-program.md`
is about. That finding named the shape; this table sizes it.
